"use client";
import React from "react";

interface PromptFormProps {
  prompt: string;
  setPrompt: (prompt: string) => void;
}

export default function PromptForm({ prompt, setPrompt }: PromptFormProps) {
  return (
    <div className="mb-3">
      <label className="form-label fw-bold">Your Prompt:</label>
      <textarea
        className="form-control"
        rows={5}
        placeholder="Enter your prompt here..."
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
      ></textarea>
    </div>
  );
}
