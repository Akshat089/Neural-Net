from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from groq import Groq
from pydantic import BaseModel, Field


class HumanFeedback(BaseModel):
    """Represents human feedback that can be injected into any iteration."""

    author: str = Field(
        default="strategist",
        description="Name or role for attribution in the feedback thread.",
    )
    message: str = Field(..., description="Specific guidance for the optimizer.")
    iteration: Optional[int] = Field(
        default=None,
        ge=1,
        description="Target iteration. Leave empty to apply to every loop.",
    )


class XPostInput(BaseModel):
    """Request body coming from the frontend."""

    topic: str = Field(..., description="Main subject or hook for the post.")
    objective: str = Field(
        ...,
        description="What success looks like for this post (e.g., clicks, hype).",
    )
    audience: str = Field(..., description="Intended audience details.")
    tone: str = Field(default="Bold", description="Stylistic direction.")
    brand_voice: str = Field(
        default="Witty, high-signal startup voice",
        description="Optional brand voice references.",
    )
    call_to_action: Optional[str] = Field(
        default=None, description="CTA to highlight inside the copy."
    )
    product_details: Optional[str] = Field(
        default=None, description="Feature details or proof points."
    )
    keywords: List[str] = Field(
        default_factory=list, description="Terms/hashtags that must appear."
    )
    word_limit: int = Field(
        default=280,
        ge=120,
        le=400,
        description="Character budget for an X post.",
    )
    max_iterations: int = Field(
        default=2,
        ge=1,
        le=5,
        description="Number of generator/evaluator/optimizer loops to run.",
    )
    human_feedback: List[HumanFeedback] = Field(
        default_factory=list,
        description="Optional operator instructions to blend into optimization.",
    )


class XPostIdeaRequest(BaseModel):
    """Request schema for the trending idea generator."""

    keywords: List[str] = Field(
        default_factory=list,
        description="Optional keywords or niches to bias the trending ideas.",
    )
    count: int = Field(
        default=4,
        ge=1,
        le=6,
        description="How many idea cards to generate.",
    )


class XPostAgent:
    """Runs a small LangChain-free loop across three Groq-hosted models."""

    def __init__(self) -> None:
        self.client = Groq()
        self.generator_model = "llama-3.3-70b-versatile"
        self.evaluator_model = "llama-3.1-8b-instant"
        self.optimizer_model = "llama-3.3-70b-versatile"
        self.approval_threshold = 4

    def invoke(self, payload: XPostInput) -> Dict[str, Any]:
        """Entry-point used by the FastAPI router."""
        iterations: List[Dict[str, Any]] = []
        feedback_threads: List[Dict[str, Any]] = []

        current_post: Optional[str] = None

        for iteration in range(1, payload.max_iterations + 1):
            generated = self._generate_post(
                payload, previous_post=current_post, round_number=iteration
            )

            evaluation = self._evaluate_post(payload, generated, iteration)
            human_feedback = self._collect_human_feedback(
                payload.human_feedback, iteration
            )

            optimized = self._optimize_post(
                payload=payload,
                latest_draft=generated,
                evaluation=evaluation,
                human_feedback=human_feedback,
                previous_best=current_post,
            )

            if not optimized:
                optimized = generated

            iterations.append(
                {
                    "iteration": iteration,
                    "generator_output": generated,
                    "evaluator_score": evaluation["score"],
                    "evaluator_verdict": evaluation["verdict"],
                    "evaluator_notes": evaluation["observations"],
                    "evaluator_action_items": evaluation.get("action_items", []),
                    "human_feedback": human_feedback,
                    "optimized_post": optimized,
                }
            )

            feedback_threads.append(
                {
                    "source": "evaluator",
                    "iteration": iteration,
                    "message": evaluation["observations"],
                    "score": evaluation["score"],
                }
            )
            for fb in human_feedback:
                feedback_threads.append(
                    {
                        "source": f"human:{fb.get('author', 'strategist')}",
                        "iteration": iteration,
                        "message": fb["message"],
                    }
                )

            current_post = optimized

            if self._should_stop(evaluation):
                break

        return {
            "status": "success",
            "final_post": current_post,
            "iterations": iterations,
            "feedback_threads": feedback_threads,
            "audit_trail": {
                "topic": payload.topic,
                "objective": payload.objective,
                "audience": payload.audience,
                "models": {
                    "generator": self.generator_model,
                    "evaluator": self.evaluator_model,
                    "optimizer": self.optimizer_model,
                },
                "total_iterations": len(iterations),
                "word_limit": payload.word_limit,
            },
        }

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #
    def _should_stop(self, evaluation: Dict[str, Any]) -> bool:
        verdict = evaluation.get("verdict", "").lower()
        score = evaluation.get("score", 0)
        return score >= self.approval_threshold and verdict.startswith("approve")

    def _generate_post(
        self,
        payload: XPostInput,
        *,
        previous_post: Optional[str],
        round_number: int,
    ) -> str:
        system_prompt = (
            "You are a growth marketer who writes concise, viral-ready posts for X."
            " Favor clarity over gimmicks, use plain language, and keep the energy high."
        )

        keywords = ", ".join(payload.keywords) if payload.keywords else "None"
        base_prompt = f"""
Round: {round_number}
Topic: {payload.topic}
Objective: {payload.objective}
Audience: {payload.audience}
Tone: {payload.tone}
Brand Voice: {payload.brand_voice}
Call to action: {payload.call_to_action or "None"}
Product proof points: {payload.product_details or "None"}
Required keywords/hashtags: {keywords}
Character budget: {payload.word_limit}

Write a single X post (no thread) that balances the above requirements.
Use punchy short sentences, keep emojis minimal (max 1) unless absolutely justified, 
and ensure the copy is <= {payload.word_limit} characters.
"""
        if previous_post:
            base_prompt += (
                "\nHere is the previous attempt. Improve on the framing while keeping"
                " any elements that clearly worked:\n"
                f"{previous_post}\n"
            )

        return self._chat_completion(
            model=self.generator_model,
            system=system_prompt,
            user=base_prompt,
            temperature=0.8 if round_number == 1 else 0.6,
            max_tokens=600,
        )

    def _evaluate_post(
        self, payload: XPostInput, draft: str, iteration: int
    ) -> Dict[str, Any]:
        system_prompt = (
            "You are a meticulous social editor who grades X posts."
            " Always respond with strict JSON."
        )

        user_prompt = f"""
Evaluate the following X post and respond using JSON with this schema:
{{
  "verdict": "APPROVED or REVISE",
  "score": integer 1-5,
  "observations": "1 paragraph summary of strengths and issues",
  "action_items": ["bullet improvements", "..."]
}}

Context:
- Topic: {payload.topic}
- Objective: {payload.objective}
- Audience: {payload.audience}
- Tone: {payload.tone}
- Keywords that must appear: {", ".join(payload.keywords) if payload.keywords else "None"}
- Character budget: {payload.word_limit}
- Iteration: {iteration}

Draft to evaluate:
{draft}
"""
        response = self._chat_completion(
            model=self.evaluator_model,
            system=system_prompt,
            user=user_prompt,
            temperature=0.2,
            max_tokens=500,
        )

        try:
            parsed = json.loads(response)
        except json.JSONDecodeError:
            parsed = {
                "verdict": "REVISE",
                "score": 3,
                "observations": response,
                "action_items": [],
            }

        parsed.setdefault("verdict", "REVISE")
        parsed.setdefault("score", 3)
        parsed.setdefault("observations", "")
        parsed.setdefault("action_items", [])
        return parsed

    def _collect_human_feedback(
        self, feedback_items: List[HumanFeedback], iteration: int
    ) -> List[Dict[str, Any]]:
        collected: List[Dict[str, Any]] = []
        for fb in feedback_items:
            if fb.iteration is None or fb.iteration == iteration:
                collected.append(
                    {
                        "author": fb.author,
                        "message": fb.message,
                        "iteration": fb.iteration,
                    }
                )
        return collected

    def _optimize_post(
        self,
        *,
        payload: XPostInput,
        latest_draft: str,
        evaluation: Dict[str, Any],
        human_feedback: List[Dict[str, Any]],
        previous_best: Optional[str],
    ) -> str:
        system_prompt = (
            "You are a collaborative copy editor who rewrites X posts with precision."
            " Blend automated and human reviewer feedback and return a single"
            " publication-ready post that honors the character budget."
        )

        human_notes = (
            "\n".join(
                f"- {item['author']}: {item['message']}" for item in human_feedback
            )
            if human_feedback
            else "None supplied."
        )

        evaluator_summary = f"""
Verdict: {evaluation.get('verdict')}
Score: {evaluation.get('score')}
Observations: {evaluation.get('observations')}
Action items: {', '.join(evaluation.get('action_items', [])) or 'None'}
"""

        user_prompt = f"""
Latest generator draft:
{latest_draft}

Previous best draft (if any):
{previous_best or "None"}

Evaluator feedback:
{evaluator_summary}

Human feedback to prioritize:
{human_notes}

Rewrite the post so it:
- stays under {payload.word_limit} characters,
- preserves the intent "{payload.objective}",
- keeps the tone "{payload.tone}" and {payload.brand_voice},
- includes these keywords if missing: {", ".join(payload.keywords) if payload.keywords else "None"},
- clearly states the CTA: {payload.call_to_action or "Implicit CTA OK"},
- feels crafted for {payload.audience}.

Return ONLY the improved X post text, no markdown fences, commentary, or numbering.
"""

        return self._chat_completion(
            model=self.optimizer_model,
            system=system_prompt,
            user=user_prompt,
            temperature=0.4,
            max_tokens=600,
        )

    def generate_trending_ideas(self, payload: XPostIdeaRequest) -> Dict[str, Any]:
        """Produce trending idea cards that the frontend can surface."""

        keywords = ", ".join(payload.keywords) if payload.keywords else "None"
        mode_instructions = (
            "Focus on emerging X trends using the provided keywords."
            if payload.keywords
            else "Pull from general startup + AI culture topics trending today."
        )

        schema = {
            "ideas": [
                {
                    "id": "short-id",
                    "headline": "catchy title",
                    "topic": "core theme",
                    "summary": "2-sentence overview",
                    "suggested_objective": "goal for the post",
                    "suggested_audience": "target persona",
                    "tone": "tone guidance",
                    "call_to_action": "CTA idea",
                    "keywords": ["keyword1", "keyword2"],
                    "hashtags": ["#tag"],
                    "sample_tweet": "tweet copy",
                }
            ]
        }

        prompt = f"""
You are a trend-spotting social strategist.

Produce {payload.count} **distinct** X post ideas. {mode_instructions}

Keywords or themes to include when relevant: {keywords}

Return STRICT JSON that matches this schema (no markdown, no prose):
{json.dumps(schema, indent=2)}

Constraints:
- Sample tweet must be under 280 characters and feel copy-ready.
- Headlines should be 6-10 words and high-signal.
- Include hashtags that would increase discoverability.
- Summaries must reference why the topic is trending **right now** (news hook, release, etc.).
"""

        raw = self._chat_completion(
            model=self.generator_model,
            system="You craft structured responses for growth teams.",
            user=prompt,
            temperature=0.65,
            max_tokens=1200,
        )

        ideas: List[Dict[str, Any]]
        try:
            parsed = json.loads(raw)
            ideas = parsed.get("ideas", [])
            if not isinstance(ideas, list):
                ideas = []
        except json.JSONDecodeError:
            ideas = []

        if not ideas:
            ideas = [
                {
                    "id": "fallback-idea",
                    "headline": "AI builders chase latency-free stacks",
                    "topic": "Ultra-fast inference week",
                    "summary": "Founders brag about 30ms generation demos after Groq's latest benchmarks shocked dev Twitter.",
                    "suggested_objective": "Drive signups to our infra explainer or waitlist.",
                    "suggested_audience": "Infra-minded AI founders and engineers",
                    "tone": "Confident, technical flex",
                    "call_to_action": "Drop your latency wins + read the breakdown",
                    "keywords": payload.keywords or ["AI infra", "low latency"],
                    "hashtags": ["#AI", "#Startups"],
                    "sample_tweet": "Dev Twitter is bragging about <50ms LLM calls. We just shipped the guide on how. Drop your latency wins + snag the blueprint. ⚡️",
                }
            ]

        return {"ideas": ideas}

    def _chat_completion(
        self,
        *,
        model: str,
        system: str,
        user: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        completion = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=temperature,
            max_completion_tokens=max_tokens,
            top_p=0.9,
            stream=False,
        )
        content = completion.choices[0].message.content
        return content.strip() if content else ""


__all__ = ["XPostAgent", "XPostInput", "HumanFeedback", "XPostIdeaRequest"]
