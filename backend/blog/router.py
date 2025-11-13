from fastapi import APIRouter, HTTPException, Request

router = APIRouter(tags=["Blog"])

@router.post("/generate-blog")
async def generate_blog(request: Request):
    """Temporary dummy endpoint — just echoes back the received data."""
    try:
        payload = await request.json()
        print("Received payload:", payload)  # Debugging log

        # Return exactly what frontend sent
        return {
            "generated_blog": f"Dummy blog for topic '{payload.get('prompt', 'N/A')}' "
                      f"with {payload.get('mediumWordCount', 'N/A')} words.",
            "received_data": payload
        }


    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
