import asyncio
from agents.draft_agent import draft_agent

async def test_agno_draft_agent():
    """Test the Agno AI-powered draft agent."""
    
    print("🧪 Testing Agno AI Draft Agent\n")
    
    # Test 1: Generate initial draft
    print("=" * 60)
    print("TEST 1: Initial Draft Generation")
    print("=" * 60)
    
    initial_prompt = """I'm organizing a Counter Strike LAN event in Mumbai for 4 days. 
Need a social media campaign targeting gamers aged 18-30."""
    
    try:
        draft = await draft_agent.generate_initial_draft(
            initial_prompt=initial_prompt,
            user_id="test-user-123"
        )
        
        print("\n✅ Draft Generated:")
        print(f"Title: {draft['title']}")
        print(f"Platforms: {draft['platforms']}")
        print(f"Target Audience: {draft['target_audience'][:100]}...")
        print(f"Color Scheme: {draft['color_scheme']}")
        print(f"Days Scheduled: {len(draft['posting_schedule'])}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return
    
    # Test 2: Refine draft
    print("\n" + "=" * 60)
    print("TEST 2: Draft Refinement")
    print("=" * 60)
    
    try:
        conversation_history = [
            {"role": "user", "content": initial_prompt},
            {"role": "assistant", "content": "I've created your campaign strategy!"}
        ]
        
        refinement_request = "Can you add TikTok to the platforms and make the color scheme more vibrant?"
        
        refined_draft = await draft_agent.refine_draft(
            current_draft=draft,
            user_message=refinement_request,
            conversation_history=conversation_history
        )
        
        print("\n✅ Draft Refined:")
        print(f"Updated Platforms: {refined_draft['platforms']}")
        print(f"Updated Colors: {refined_draft['color_scheme']}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return
    
    # Test 3: Conversational response
    print("\n" + "=" * 60)
    print("TEST 3: Conversational Response (with memory)")
    print("=" * 60)
    
    try:
        response = await draft_agent.generate_conversational_response(
            draft=refined_draft,
            user_message=refinement_request,
            conversation_history=conversation_history,
            campaign_id="test-campaign-123"
        )
        
        print("\n✅ Conversational Response:")
        print(response)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ All Tests Complete!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_agno_draft_agent())