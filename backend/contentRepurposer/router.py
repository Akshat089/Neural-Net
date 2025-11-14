from fastapi import APIRouter, HTTPException
from .agent_content_repurposer_workflow import ContentRepurposerAgent, RepurposerInput

# -------------------------------
# Initialize Router & Agent
# -------------------------------
router = APIRouter(tags=["Content Repurposer"])

# Initialize Repurposer Agent
# This agent loads the graph when it's created
repurposer_agent = ContentRepurposerAgent()

# -------------------------------
# Content Repurposer Endpoint
# -------------------------------
@router.post("/repurpose-article")
def repurpose_article(input_data: RepurposerInput):
    """
    Receives article text, validates it, and runs the 
    parallel content repurposing workflow.
    
    The frontend sends:
    { "article_text": "..." }
    
    This endpoint returns:
    { "status": "success", "repurposed_content": { ... } }
    """
    try:
        # Debug log to see the incoming text (truncated)
        print("Received repurposer payload:", input_data.article_text[:100] + "...") 

        # Use the synchronous 'invoke' method from the agent
        # FastAPI will run this sync function in a threadpool
        result = repurposer_agent.invoke(input_data)

        # The agent's error handling returns an 'error' key
        if "error" in result:
            print(f"Error in /repurpose-article: {result['error']}")
            raise HTTPException(status_code=500, detail=result["error"])

        # Success: return the package the frontend expects
        # The agent already formats this as: {"repurposed_content": ...}
        return {
            "status": "success",
            **result  # This unpacks to {"repurposed_content": ...}
        }

    except Exception as e:
        print(f"Unhandled error in /repurpose-article: {e}")
        raise HTTPException(status_code=500, detail=str(e))