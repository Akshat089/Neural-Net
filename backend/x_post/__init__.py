"""
Backend package for the X post workflow.

Holds the FastAPI router plus the Groq-powered agent that orchestrates the
generator / evaluator / optimizer loop. The directory previously only
contained experimentation notebooks, so this module wires those ideas into
production code.
"""

