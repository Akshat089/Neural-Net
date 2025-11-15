from fastapi import APIRouter, HTTPException, Request
from .agent_youtube_script import YoutubeScriptAgent
from pydantic import BaseModel
import uuid
from .youtube_script_model import generate

router = APIRouter(tags=["YouTube Script"])

agent = YoutubeScriptAgent()
agent.compile()


@router.post("/generate-youtube-script")
async def generate_youtube_script(request: Request):
    """Receives frontend JSON and runs the YouTube script workflow."""
    try:
        payload = await request.json()
        print("Received payload:", payload)

        # Generate thread ID
        thread_id = str(uuid.uuid4())
        payload["threadId"] = thread_id

        print("Payload passed to agent:", payload)

        # Run agent
        result = await agent.ainvoke(payload)

        return {
            "status": "success",
            "threadId": thread_id,
            "generated_script": result.get("data", {}).get("script", "No script generated"),
            "revision_count": result.get("data", {}).get("revision_count", 0),
            "received_data": payload
        }

    except Exception as e:
        print("🔥 Error:", e)
        raise HTTPException(status_code=500, detail=str(e))

class ImagePromptRequest(BaseModel):
    channelDescription: str = ""
    prompt: str = ""              # Video topic
    script: str = ""              # Generated script
    tone: str = ""
    audience: str = ""


@router.post("/image-prompt")
def craft_image_prompt(payload: ImagePromptRequest):
    """Generate an SDXL-friendly thumbnail prompt for YouTube videos."""
    try:
        template = f"""
        You are a world-class YouTube creative director who specializes in designing
        high-conversion thumbnails that stand out on the homepage.

        Use the following context to craft a single-paragraph SDXL prompt:

        Channel Description:
        {payload.channelDescription or "Not provided"}

        Video Topic:
        {payload.prompt or "No topic provided"}

        Script Summary:
        {payload.script[:500] if payload.script else "No script provided"}

        Tone: {payload.tone or "Not provided"}
        Target Audience: {payload.audience or "Not provided"}

        --- RULES ---
        • Describe an eye-catching YouTube thumbnail scene.
        • Include emotion, character expression, text placement ideas.
        • Include lighting, colors, environment, and camera angle.
        • Must reflect the theme of the script.
        • DO NOT mention “prompt” or repeat the instructions.
        • Limit to 120 words.
        """

        prompt_text = generate(template, max_tokens=256, temperature=0.7)
        return {"image_prompt": prompt_text.strip()}

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
