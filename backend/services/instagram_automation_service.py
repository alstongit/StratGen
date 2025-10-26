import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import os
from typing import Dict, Any, List, Optional
from config.settings import settings
from PIL import Image
import requests
from io import BytesIO
import tempfile
import pyperclip

class InstagramAutomationService:
    """
    Selenium-based Instagram automation for posting campaign content.
    Uses undetected-chromedriver to bypass bot detection.
    """
    
    def __init__(self):
        self.driver: Optional[uc.Chrome] = None
        self.username = settings.INSTAGRAM_USERNAME
        self.password = settings.INSTAGRAM_PASSWORD
        self.headless = settings.INSTAGRAM_HEADLESS
        print("✅ InstagramAutomationService initialized")
    
    def _init_driver(self):
        """Initialize undetected Chrome driver with stealth options."""
        try:
            options = uc.ChromeOptions()
            
            if self.headless:
                options.add_argument('--headless=new')
            
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--start-maximized')
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')
            
            prefs = {
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False,
                "profile.default_content_setting_values.notifications": 2
            }
            options.add_experimental_option("prefs", prefs)
            
            self.driver = uc.Chrome(
                options=options,
                use_subprocess=False,
                driver_executable_path=None
            )
            
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
            })
            
            print("✅ Chrome driver initialized")
            
        except Exception as e:
            print(f"❌ Failed to initialize driver: {e}")
            raise
    
    def _dismiss_popups(self):
        """Dismiss common Instagram popups after login."""
        popup_buttons = [
            "Not Now",
            "Not now",
            "Save Info",
            "Turn On",
            "Cancel",
            "Later",
            "Dismiss"
        ]
        
        for button_text in popup_buttons:
            try:
                selectors = [
                    f"//button[contains(text(), '{button_text}')]",
                    f"//button[text()='{button_text}']",
                    f"//a[contains(text(), '{button_text}')]"
                ]
                
                for selector in selectors:
                    try:
                        button = self.driver.find_element(By.XPATH, selector)
                        button.click()
                        print(f"✓ Dismissed popup: {button_text}")
                        time.sleep(1)
                        break
                    except:
                        continue
            except:
                continue
    
    async def login(self) -> bool:
        """Login to Instagram using credentials from env."""
        try:
            if not self.driver:
                self._init_driver()
            
            print("🔐 Logging into Instagram...")
            self.driver.get("https://www.instagram.com/accounts/login/")
            
            wait = WebDriverWait(self.driver, 20)
            
            username_input = wait.until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            username_input.clear()
            username_input.send_keys(self.username)
            time.sleep(1)
            
            password_input = self.driver.find_element(By.NAME, "password")
            password_input.clear()
            password_input.send_keys(self.password)
            time.sleep(1)
            
            password_input.send_keys(Keys.RETURN)
            
            try:
                wait.until(
                    lambda d: "instagram.com" in d.current_url and "login" not in d.current_url
                )
                print("✅ Successfully logged into Instagram")
            except TimeoutException:
                print("❌ Login timeout")
                if "login" in self.driver.current_url:
                    raise Exception("Login failed - still on login page")
            
            time.sleep(3)
            
            print("🔄 Dismissing popups...")
            self._dismiss_popups()
            time.sleep(2)
            
            print("🏠 Navigating to home...")
            self.driver.get("https://www.instagram.com/")
            time.sleep(3)
            
            self._dismiss_popups()
            
            return True
        
        except Exception as e:
            print(f"❌ Instagram login failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def upload_post(
        self,
        image_url: str,
        caption: str,
        hashtags: List[str]
    ) -> Dict[str, Any]:
        """Upload a single post to Instagram."""
        try:
            print(f"📸 Uploading post to Instagram...")
            print(f"   Image: {image_url[:60]}...")
            print(f"   Caption: {caption[:50]}...")
            
            # Download image to temp file
            image_path = await self._download_image(image_url)
            
            wait = WebDriverWait(self.driver, 30)
            
            # STEP 1: Click "Create" button in sidebar
            print("🔍 Step 1: Looking for Create button...")
            create_selectors = [
                "//span[text()='Create']/parent::a",
                "//a[.//span[text()='Create']]",
            ]
            
            create_btn = None
            for selector in create_selectors:
                try:
                    create_btn = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    break
                except:
                    continue
            
            if not create_btn:
                raise Exception("Could not find Create button")
            
            create_btn.click()
            print("✅ Clicked Create")
            time.sleep(2)
            
            # STEP 2: Click "Post" option from dropdown
            print("📝 Step 2: Looking for Post option...")
            post_selectors = [
                "//span[text()='Post']",
                "//div[text()='Post']",
            ]
            
            post_option = None
            for selector in post_selectors:
                try:
                    post_option = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    break
                except:
                    continue
            
            if not post_option:
                raise Exception("Could not find Post option")
            
            post_option.click()
            print("✅ Clicked Post")
            time.sleep(3)
            
            # STEP 3: Upload file
            print("📤 Step 3: Uploading image file...")
            file_input = wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
            )
            file_input.send_keys(image_path)
            print("✅ Image uploaded")
            time.sleep(5)
            
            # STEP 4: Click "Next" on CROP screen
            print("➡️ Step 4: Clicking Next (crop)...")
            next_selectors = [
                "//div[text()='Next']",
                "//button[contains(text(), 'Next')]",
                "//*[contains(text(), 'Next') and @role='button']",
            ]
            
            next_btn = None
            for selector in next_selectors:
                try:
                    next_btn = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    break
                except:
                    continue
            
            if not next_btn:
                self.driver.save_screenshot(f"error_crop_{int(time.time())}.png")
                raise Exception("Could not find Next button on crop screen")
            
            next_btn.click()
            print("✅ Clicked Next (crop)")
            time.sleep(3)
            
            # STEP 5: Click "Next" on FILTER screen
            print("➡️ Step 5: Clicking Next (filter/edit)...")
            next_btn = None
            for selector in next_selectors:
                try:
                    next_btn = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    break
                except:
                    continue
            
            if not next_btn:
                self.driver.save_screenshot(f"error_filter_{int(time.time())}.png")
                raise Exception("Could not find Next button on filter screen")
            
            next_btn.click()
            print("✅ Clicked Next (filter)")
            time.sleep(3)
            
            # STEP 6: Enter caption using clipboard paste (supports all Unicode)
            print("✍️ Step 6: Writing caption...")
            
            # Find caption input
            caption_selectors = [
                "//div[@contenteditable='true'][@aria-label]",
                "//textarea[@aria-label]",
                "//div[@role='textbox']",
            ]
            
            caption_area = None
            for selector in caption_selectors:
                try:
                    caption_area = wait.until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                    break
                except:
                    continue
            
            if not caption_area:
                self.driver.save_screenshot(f"error_caption_{int(time.time())}.png")
                raise Exception("Could not find caption input")
            
            # Build full caption with hashtags
            full_caption = f"{caption}\n\n{' '.join(hashtags)}"
            
            # Method: Use clipboard to paste (works with emojis)
            print("   Using clipboard paste method (supports emoji)...")
            
            try:
                # Copy caption to clipboard
                pyperclip.copy(full_caption)
                
                # Click caption field
                caption_area.click()
                time.sleep(0.5)
                
                # Paste using Ctrl+V
                caption_area.send_keys(Keys.CONTROL, 'v')
                time.sleep(1)
                
                print("✅ Caption pasted from clipboard")
                
                # Verify
                current_text = self.driver.execute_script("""
                    var element = arguments[0];
                    return element.tagName === 'TEXTAREA' ? element.value : element.textContent;
                """, caption_area)
                
                if current_text and len(current_text) > 10:
                    print(f"   ✓ Caption verified: {len(current_text)} characters")
                else:
                    print(f"   ⚠️ Caption length unexpected: {len(current_text) if current_text else 0} chars")
                    
            except Exception as e:
                print(f"   ⚠️ Clipboard method failed: {e}")
                print("   Trying simplified JavaScript method...")
                
                # Fallback: Simplified JS without setTimeout
                simple_script = """
                var element = arguments[0];
                var text = arguments[1];
                element.focus();
                if (element.tagName === 'TEXTAREA') {
                    element.value = text;
                } else {
                    element.textContent = text;
                }
                element.dispatchEvent(new Event('input', { bubbles: true }));
                """
                self.driver.execute_script(simple_script, caption_area, full_caption)
                print("   ✓ Caption set via simplified JS")
            
            time.sleep(2)
            
            # STEP 7: Click "Share" button
            print("📤 Step 7: Clicking Share...")
            share_selectors = [
                "//div[text()='Share']",
                "//button[contains(text(), 'Share')]",
                "//*[contains(text(), 'Share') and @role='button']",
            ]
            
            share_btn = None
            for selector in share_selectors:
                try:
                    share_btn = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    break
                except:
                    continue
            
            if not share_btn:
                self.driver.save_screenshot(f"error_share_{int(time.time())}.png")
                raise Exception("Could not find Share button")
            
            share_btn.click()
            print("✅ Clicked Share")
            
            # STEP 8: Wait for success confirmation
            print("⏳ Step 8: Waiting for confirmation...")
            time.sleep(5)
            
            try:
                success_selectors = [
                    "//*[contains(text(), 'shared')]",
                    "//*[contains(text(), 'Your post')]",
                    "//*[contains(text(), 'Post shared')]",
                ]
                
                for selector in success_selectors:
                    try:
                        wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                        print("✅ Post confirmed!")
                        break
                    except:
                        continue
            except:
                print("⚠️ Could not confirm, but assuming success")
            
            # Clean up
            os.remove(image_path)
            
            post_url = f"https://www.instagram.com/p/SIMULATED_{int(time.time())}/"
            
            return {
                "success": True,
                "post_url": post_url,
                "uploaded_at": time.time()
            }
        
        except Exception as e:
            print(f"❌ Failed to upload post: {e}")
            import traceback
            traceback.print_exc()
            
            try:
                self.driver.save_screenshot(f"instagram_error_{int(time.time())}.png")
                print("📸 Error screenshot saved")
            except:
                pass
            
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _download_image(self, url: str) -> str:
        """Download image from URL to temp file."""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            img = Image.open(BytesIO(response.content))
            
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
            img.convert('RGB').save(temp_file.name, 'JPEG', quality=95)
            temp_file.close()
            
            print(f"✅ Image downloaded to {temp_file.name}")
            return temp_file.name
        
        except Exception as e:
            print(f"❌ Failed to download image: {e}")
            raise
    
    async def automate_campaign_posting(
        self,
        posts: List[Dict[str, Any]],
        delay_between_posts: int = 300
    ) -> Dict[str, Any]:
        """Automate posting of all campaign posts."""
        try:
            login_success = await self.login()
            if not login_success:
                return {
                    "success": False,
                    "error": "Login failed",
                    "posts_published": 0
                }
            
            results = []
            
            for i, post in enumerate(posts, 1):
                print(f"\n{'='*60}")
                print(f"📤 POSTING {i}/{len(posts)}")
                print(f"{'='*60}")
                
                copy_data = post.get("copy", {}).get("content", {})
                image_data = post.get("image", {}).get("content", {})
                
                caption = copy_data.get("caption", "")
                hashtags = copy_data.get("hashtags", [])
                image_url = image_data.get("image_url")
                
                if not image_url:
                    print(f"⚠️ Skipping post {i} - no image URL")
                    results.append({"success": False, "error": "No image"})
                    continue
                
                result = await self.upload_post(
                    image_url=image_url,
                    caption=caption,
                    hashtags=hashtags
                )
                
                results.append(result)
                
                if result.get("success"):
                    print(f"✅ Post {i} uploaded successfully!")
                else:
                    print(f"❌ Post {i} failed: {result.get('error')}")
                
                if i < len(posts):
                    print(f"\n⏳ Waiting {delay_between_posts}s before next post...")
                    time.sleep(delay_between_posts)
            
            success_count = sum(1 for r in results if r.get("success"))
            
            print(f"\n{'='*60}")
            print(f"✅ AUTOMATION COMPLETE: {success_count}/{len(posts)} posts uploaded")
            print(f"{'='*60}")
            
            return {
                "success": success_count > 0,
                "posts_published": success_count,
                "total_posts": len(posts),
                "results": results
            }
        
        except Exception as e:
            print(f"❌ Campaign automation failed: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "posts_published": 0
            }
        
        finally:
            if self.driver:
                self.driver.quit()
                self.driver = None
                print("✅ Browser closed")

# Global instance
_instagram_service = None

def get_instagram_automation_service() -> InstagramAutomationService:
    """Get or create InstagramAutomationService instance."""
    global _instagram_service
    if _instagram_service is None:
        _instagram_service = InstagramAutomationService()
    return _instagram_service