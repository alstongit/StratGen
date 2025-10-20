import asyncio
from agents.draft_agent import draft_agent

async def test_draft_generation():
    """Test the draft agent."""
    
    print("🧪 Testing Draft Agent with Gemini 2.0 Flash...\n")
    
    # Test 1: Initial draft generation
    print("📝 Test 1: Generating initial draft...")
    try:
        draft = await draft_agent.generate_initial_draft(
            initial_prompt="Counter Strike LAN event in Mumbai for 4 days, targeting gamers aged 18-30",
            user_id="test-user-123"
        )
        print("✅ Draft generated successfully!")
        print(f"Title: {draft.get('title')}")
        print(f"Target Audience: {draft.get('target_audience')}")
        print(f"Platforms: {draft.get('platforms')}")
        print(f"Colors: {draft.get('color_scheme')}")
        print()
    except Exception as e:
        print(f"❌ Error: {e}\n")
        return
    
    # Test 2: Conversational response
    print("💬 Test 2: Generating conversational response...")
    try:
        response = await draft_agent.generate_conversational_response(
            draft=draft,
            user_message="Counter Strike LAN event in Mumbai for 4 days",
            conversation_history=[]
        )
        print("✅ Response generated!")
        print(f"Response: {response}")
        print()
    except Exception as e:
        print(f"❌ Error: {e}\n")
    
    # Test 3: Refining draft
    print("🔧 Test 3: Refining draft...")
    try:
        refined_draft = await draft_agent.refine_draft(
            current_draft=draft,
            user_message="Make it more focused on competitive gaming and add more aggressive colors",
            conversation_history=[
                {"role": "user", "content": "Counter Strike LAN event in Mumbai for 4 days"},
                {"role": "assistant", "content": "I've created a strategy for your event!"}
            ]
        )
        print("✅ Draft refined successfully!")
        print(f"Updated Colors: {refined_draft.get('color_scheme')}")
        print(f"Updated Themes: {refined_draft.get('content_themes')}")
        print()
    except Exception as e:
        print(f"❌ Error: {e}\n")
    
    print("✨ All tests completed!")

if __name__ == "__main__":
    asyncio.run(test_draft_generation())