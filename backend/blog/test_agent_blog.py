# test_agent_blog.py
import asyncio
from agent_blog_workflow import BlogWorkflowAgent

async def main():
    # Instantiate and compile the agent
    agent = BlogWorkflowAgent()
    agent.compile()

    # Example input simulating frontend payload
    test_input = {
        "brand_name": "Acme Corp",
        "brand_voice": "Friendly and professional",
        "prompt": "Write a blog about the future of AI in healthcare.",
        "tone": "informative",
        "audience": "tech professionals",
        "modalities": {
            "medium": 600,
            "linkedin": 200,
            "twitter": 100,
            "threads": 150
        }
    }

    # Run the agent workflow
    result = await agent.ainvoke(test_input)
    
    # Print the formatted output
    print("=== Result ===")
    if result.get("status") == "success":
        print(result["data"]["formatted_blog"])
        print("\n--- Raw Output ---")
        print(result["data"]["raw_result"])
    else:
        print("Error:", result.get("message"))

if __name__ == "__main__":
    asyncio.run(main())
