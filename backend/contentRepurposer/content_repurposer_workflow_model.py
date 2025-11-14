import json
from typing import Dict, Any, List
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# -------------------------------
# Initialize Groq client
# -------------------------------
client = Groq()  # Uses GROQ_API_KEY from environment


def generate_fast_response(prompt: str, max_tokens=1024, temperature=0.2) -> str:
    """Uses the fast Groq model for simple generation tasks."""
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_completion_tokens=max_tokens,
        top_p=1,
        stream=False,
    )
    return completion.choices[0].message.content.strip()


def generate_json_response(prompt: str, max_tokens=1024, temperature=0.1) -> Dict:
    """Uses the fast Groq model with JSON mode for structured output."""
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_completion_tokens=max_tokens,
        top_p=1,
        stream=False,
        response_format={"type": "json_object"},
    )
    try:
        return json.loads(completion.choices[0].message.content.strip())
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON from model response.")
        return {}


# -------------------------------
# State Schema
# -------------------------------
class RepurposerState(BaseModel):
    """
    State for the content repurposing workflow.
    Mirrors the 'RepurposeResults' interface on the frontend.
    """
    # 🧠 Input from frontend
    article_text: str

    # 🔄 Workflow-generated fields (the parallel outputs)
    summary: str | None = None
    social_posts: Dict[str, str] | None = None # <-- Expects Dict[str, str]
    faq_section: str | None = None
    entities: Dict[str, List[str]] | None = None
    
    # 📦 Final package for the frontend
    final_package: Dict[str, Any] | None = None


# -------------------------------
# Parallel Nodes
# -------------------------------

def generate_summary(state: RepurposerState) -> Dict[str, Any]:
    """Node 1: Generates a concise summary of the article."""
    print("--- 1. GENERATING SUMMARY ---")
    prompt = f"""
You are a concise editor. Summarize the following article in one compelling paragraph (about 100-150 words).
The summary should capture the main points and be suitable for a preview.

ARTICLE:
{state.article_text}
"""
    summary = generate_fast_response(prompt, 512)
    return {"summary": summary}


def generate_social_posts(state: RepurposerState) -> Dict[str, Any]:
    """Node 2: Generates social media posts in a JSON object."""
    print("--- 2. GENERATING SOCIAL POSTS ---")
    
    # --- FIX 1: Updated Prompt ---
    # Be explicit that the *value* must be a string.
    prompt = f"""
You are a social media manager. Analyze the following article and generate a JSON object for social media posts.
The JSON object must have keys: "twitter", "linkedin", and "instagram".
The **value** for each key must be a **single string** containing the post text.

Example format:
{{
  "twitter": "This is the tweet text.",
  "linkedin": "This is the LinkedIn post text.",
  "instagram": "This is the Instagram caption text."
}}

1.  "twitter" (string): A compelling 280-character tweet with a strong hook and 2-3 relevant hashtags.
2.  "linkedin" (string): A professional post (~100-150 words) for LinkedIn, focusing on the key insights and ending with a question.
3.  "instagram" (string): An engaging Instagram caption (~50-100 words) that teases the content and includes 5 relevant hashtags.

ARTICLE:
{state.article_text}
"""
    social_posts = generate_json_response(prompt, 1024)

    # --- FIX 2: Add Helper to Clean AI Output ---
    # This will safely extract the text, even if the AI
    # still returns {"text": "..."} by mistake.
    
    def extract_text(post_data: Any) -> str:
        """Helper to extract text, whether it's a string or a dict."""
        if isinstance(post_data, str):
            return post_data
        if isinstance(post_data, dict) and "text" in post_data:
            return post_data["text"]
        
        # Fallback if the key is missing or format is wrong
        return "Failed to generate post."

    # Use the helper to build the valid dictionary
    valid_posts = {
        "twitter": extract_text(social_posts.get("twitter")),
        "linkedin": extract_text(social_posts.get("linkedin")),
        "instagram": extract_text(social_posts.get("instagram")),
    }
    
    return {"social_posts": valid_posts}


def generate_faq_section(state: RepurposerState) -> Dict[str, Any]:
    """Node 3: Generates an SEO-friendly FAQ section."""
    print("--- 3. GENERATING FAQ SECTION ---")
    prompt = f"""
You are an SEO specialist. Read the following article and generate a 'Frequently Asked Questions' (FAQ) section.
It should contain 3-5 questions and their answers based *only* on the article's content.
Format the output as simple Markdown (e.g., "**Q: Question?**\nA: Answer.").

ARTICLE:
{state.article_text}
"""
    faq_section = generate_fast_response(prompt, 1024)
    return {"faq_section": faq_section}


def generate_entities(state: RepurposerState) -> Dict[str, Any]:
    """Node 4: Extracts keywords and entities as a JSON object."""
    print("--- 4. EXTRACTING KEYWORDS/ENTITIES ---")
    prompt = f"""
You are a data analyst. Extract key entities from the following article.
Return a JSON object with three keys:
1.  "people": A list of all person names mentioned. (e.g., ["Jane Doe", "John Smith"])
2.  "organizations": A list of all company, government, or group names. (e.g., ["Acme Corp", "The UN"])
3.  "topics": A list of 5-10 key topics or keywords. (e.g., ["AI", "Machine Learning", "Data Privacy"])

Return empty lists if none are found.

ARTICLE:
{state.article_text}
"""
    entities = generate_json_response(prompt, 1024)
    # Ensure the structure matches the frontend expectation
    valid_entities = {
        "people": entities.get("people", []),
        "organizations": entities.get("organizations", []),
        "topics": entities.get("topics", []),
    }
    return {"entities": valid_entities}


# -------------------------------
# "Join" Node (Compile Package)
# -------------------------------

def compile_package(state: RepurposerState) -> Dict[str, Any]:
    """
    This node runs *after* all parallel nodes are complete.
    It assembles the final package that matches the frontend's expected structure.
    """
    print("--- 5. COMPILING FINAL PACKAGE ---")
    
    # This structure must match 'RepurposeResults' in the frontend
    final_package = {
        "summary": state.summary,
        "social_posts": state.social_posts,
        "faq_section": state.faq_section,
        "entities": state.entities,
    }
    
    return {"final_package": final_package}


# -------------------------------
# Build the Graph
# -------------------------------
def build_repurposer_graph() -> StateGraph:
    """Builds the parallel workflow for repurposing content."""
    
    graph = StateGraph(RepurposerState)

    # 1. Add all the nodes
    graph.add_node("generate_summary", generate_summary)
    graph.add_node("generate_social_posts", generate_social_posts)
    graph.add_node("generate_faq_section", generate_faq_section)
    graph.add_node("generate_entities", generate_entities)
    graph.add_node("compile_package", compile_package)

    # 2. Define the graph flow
    
    # START node branches out to all 4 tasks, which run in parallel
    graph.add_edge(START, "generate_summary")
    graph.add_edge(START, "generate_social_posts")
    graph.add_edge(START, "generate_faq_section")
    graph.add_edge(START, "generate_entities")

    # 3. Define the "join" point
    # We create a "join" edge that waits for all 4 parallel tasks
    # to complete before running the 'compile_package' node.
    graph.add_edge(
        [
            "generate_summary",
            "generate_social_posts",
            "generate_faq_section",
            "generate_entities",
        ],
        "compile_package",
    )

    # 4. The compile node is the last step
    graph.add_edge("compile_package", END)

    return graph.compile()