from typing import Dict, Any, Type
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field
from groq import Groq
# from langgraph.runners import GraphRunner

import os

# -------------------------------
# Initialize Groq client
# -------------------------------
client = Groq()  # Make sure GROQ_API_KEY is set in environment

def generate(prompt: str, max_tokens=512) -> str:
    """Use Groq API to generate text from prompt."""
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_completion_tokens=max_tokens,
        top_p=1,
        stream=False,
        stop=None
    )
    return completion.choices[0].message.content

# -------------------------------
# State Schema
# -------------------------------
class BlogState(BaseModel):
    messages: list = Field(default_factory=list)
    topic: str = "The Future of Remote Work"
    brief: str = ""
    word_count: int = 1000
    tone: str = "pragmatic"
    audience: str = "business decision makers"
    plan: str = None
    research_notes: str = None
    draft: str = None
    compliance_report: str = None
    revision_notes: str = None
    social_assets: str = None
    hero_prompt: str = None
    revision_count: int = 0

# -------------------------------
# Node Implementations (use Groq)
# -------------------------------
def project_plan(state: BlogState) -> Dict[str, Any]:
    prompt = f"""You are a Project Manager. Based on the topic, create a 4-step blog production plan.
Topic: {state.topic}
Tone: {state.tone}
Audience: {state.audience}
Word count: {state.word_count}
Brief: {state.brief}"""
    return {"plan": generate(prompt, 256)}

def strategy_research(state: BlogState) -> Dict[str, Any]:
    prompt = f"""You are a Research Strategist. List 3-4 credible findings or stats about {state.topic}.
Each should include short source-style attributions."""
    return {"research_notes": generate(prompt, 256)}

def draft_blog(state: BlogState) -> Dict[str, Any]:
    prompt = f"""You are a Copywriter. Write a ~{state.word_count}-word blog on the topic '{state.topic}'.
Tone: {state.tone}
Audience: {state.audience}
Include the following research:
{state.research_notes}
Format in Markdown with introduction, body (3 sections), and conclusion."""
    return {"draft": generate(prompt, 512)}

def compliance_review(state: BlogState) -> Dict[str, Any]:
    prompt = f"""You are the Compliance Reviewer (brand + legal + factual accuracy).
Review the following blog and return JSON with keys:
status (approve or revise), notes, flagged_sections.
Blog draft:
{state.draft}"""
    return {"compliance_report": generate(prompt, 256)}

def editor_feedback(state: BlogState) -> Dict[str, Any]:
    prompt = f"""You are an Editor. Summarize the compliance concerns and write revision notes for the writer.
Compliance report:
{state.compliance_report}"""
    return {"revision_notes": generate(prompt, 256), "revision_count": state.revision_count + 1}

def repurpose_assets(state: BlogState) -> Dict[str, Any]:
    prompt = f"""You are a Social Media Strategist. From this blog, generate:
1. Three tweets highlighting different key ideas.
2. One LinkedIn post summary (<= 4 paragraphs).
3. A one-sentence hero image prompt.
Blog:
{state.draft}"""
    return {"social_assets": generate(prompt, 256),
            "hero_prompt": "A futuristic workspace with holographic meeting displays."}

def finalize_package(state: BlogState) -> Dict[str, Any]:
    return {"response": "✅ Blog package ready: includes plan, research, draft, compliance, social assets."}

# -------------------------------
# Conditional routing
# -------------------------------
def route_after_compliance(state: BlogState) -> str:
    text = (state.compliance_report or "").lower()
    if "revise" in text or "flag" in text:
        return "editor_feedback"
    return "repurpose_assets"

# -------------------------------
# Build the workflow graph
# -------------------------------
def build_blog_graph() -> StateGraph:
    graph = StateGraph(BlogState)

    graph.add_node("project_plan", project_plan)
    graph.add_node("strategy_research", strategy_research)
    graph.add_node("draft_blog", draft_blog)
    graph.add_node("compliance_review", compliance_review)
    graph.add_node("editor_feedback", editor_feedback)
    graph.add_node("repurpose_assets", repurpose_assets)
    graph.add_node("finalize_package", finalize_package)

    graph.add_edge(START, "project_plan")
    graph.add_edge("project_plan", "strategy_research")
    graph.add_edge("strategy_research", "draft_blog")
    graph.add_edge("draft_blog", "compliance_review")

    graph.add_conditional_edges(
        "compliance_review",
        route_after_compliance,
        {
            "editor_feedback": "draft_blog",
            "repurpose_assets": "repurpose_assets",
        },
    )

    graph.add_edge("repurpose_assets", "finalize_package")
    graph.add_edge("finalize_package", END)

    return graph

# -------------------------------
# Example run (for testing)
# -------------------------------
if __name__ == "__main__":
    state = BlogState(topic="AI in Education", brief="Discuss how AI tools enhance learning.")

    state.plan = project_plan(state)["plan"]
    state.research_notes = strategy_research(state)["research_notes"]
    state.draft = draft_blog(state)["draft"]
    state.compliance_report = compliance_review(state)["compliance_report"]

    # Decide next node manually
    if "revise" in (state.compliance_report or "").lower():
        state.revision_notes = editor_feedback(state)["revision_notes"]
        state.revision_count += 1
        state.draft = draft_blog(state)["draft"]

    state.social_assets, state.hero_prompt = repurpose_assets(state)["social_assets"], repurpose_assets(state)["hero_prompt"]
    summary = finalize_package(state)["response"]

    print("\n--- FINAL OUTPUT ---")
    print(f"Draft: {state.draft}")
    print(f"Social Assets: {state.social_assets}")
    print(f"Hero Prompt: {state.hero_prompt}")
    print(summary)
