import asyncio
from agent_blog_workflow import BlogWorkflowAgent

async def main():
    # Create and compile the agent
    agent = BlogWorkflowAgent()
    agent.compile()

    # Dummy input (matches your frontend schema)
    input_data = {
        "brand_name": "Patagonia",
        "brand_voice": "Environmentally conscious, minimalist, and adventurous.",
        "prompt": "How sustainable design is shaping the future of outdoor gear.",
        "tone": "inspirational",
        "audience": "eco-conscious professionals and outdoor enthusiasts",
        "modalities": {
            "medium": 700,
            "linkedin": 250,
            "twitter": 100
        }
    }

    # Invoke workflow
    print("🧠 Running blog workflow...\n")
    result = await agent.ainvoke(input_data)

    # Print results
    print("\n--- WORKFLOW OUTPUT ---")
    if result["status"] == "success":
        data = result["data"]
        print(f"\n✅ Brand: {data.get('brand_name')}")
        print(f"\n📜 Brand History:\n{data.get('brand_history')}")
        print(f"\n📚 Research Notes:\n{data.get('research_notes')}")
        print(f"\n📝 Blog Draft:\n{data.get('blog_draft')[:500]}...")
        print(f"\n📣 Social Assets:\n{data.get('social_assets')}")
    else:
        print(f"❌ Error: {result['message']}")

# Run async test
asyncio.run(main())
