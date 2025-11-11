"use client";
import React, { useState } from "react";
import "bootstrap/dist/css/bootstrap.min.css";
import Navbar from "../components/ui/Navbar";
import TagSelector from "../components/generate/TagSelector";
import PromptForm from "../components/generate/PromptForm";
import { useRouter } from "next/navigation";

// --- Define Content Types and their Tags ---
const CONTENT_TYPE_TAGS: Record<string, string[]> = {
  "Blog Post": [
    "SEO Keywords",
    "Blog Intro",
    "Blog Outline",
    "LinkedIn Post",
    "Twitter Thread",
  ],
  "YouTube Script": [
    "Video Title Ideas",
    "Video Description",
    "Video Hook",
    "SEO Keywords",
    "Ad Read Script",
  ],
  "Email Newsletter": [
    "Subject Line",
    "Email Body",
    "Call to Action",
    "Social Media Snippet",
  ],
};

// Get the names of the content types
const contentTypes = Object.keys(CONTENT_TYPE_TAGS);
// ---

export default function GeneratePage() {
  const router = useRouter();

  // --- State ---
  const [contentType, setContentType] = useState(contentTypes[0]); // Default to first type
  const [prompt, setPrompt] = useState("");
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  // --- Derived State ---
  const availableTags = CONTENT_TYPE_TAGS[contentType];

  // --- Handlers ---
  const handleContentTypeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setContentType(e.target.value);
    // CRITICAL: Reset selected tags when content type changes
    setSelectedTags([]);
  };

  const handleSelectTag = (tag: string) => {
    setSelectedTags((prevTags) => [tag, ...prevTags.filter((t) => t !== tag)]);
  };

  const handleDeselectTag = (tagToDoRemove: string) => {
    setSelectedTags((prevTags) =>
      prevTags.filter((tag) => tag !== tagToDoRemove)
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    // Your logic to send the data to the AI backend
    console.log("Submitting to AI:");
    console.log("Content Type:", contentType);
    console.log("Prompt:", prompt);
    console.log("Targets:", selectedTags);

    // Example:
    // const res = await fetch(`${BACKEND_URL}/api/generate`, {
    //   method: "POST",
    //   headers: { "Content-Type": "application/json" },
    //   body: JSON.stringify({ contentType, prompt, selectedTags }),
    // });
    // const data = await res.json();

    // DUMMY DELAY to show loading
    await new Promise((resolve) => setTimeout(resolve, 1500));

    // After generation, redirect to the results page
    // You would use the real ID from the backend response
    const newContentId = "123-fake-id";
    router.push(`/content/${newContentId}`);

    setIsLoading(false);
  };

  return (
    <div>
      <Navbar />

      <div className="container mt-4">
        <div
          className="card p-4 shadow-sm mx-auto"
          style={{ maxWidth: "800px" }}
        >
          <form onSubmit={handleSubmit}>
            {/* === Content Type Selector === */}
            <div className="mb-3">
              <label htmlFor="contentTypeSelect" className="form-label fw-bold">
                Select Content Type:
              </label>
              <select
                id="contentTypeSelect"
                className="form-select"
                value={contentType}
                onChange={handleContentTypeChange}
              >
                {contentTypes.map((type) => (
                  <option key={type} value={type}>
                    {type}
                  </option>
                ))}
              </select>
            </div>

            {/* === Prompt Form === */}
            <PromptForm prompt={prompt} setPrompt={setPrompt} />

            {/* === Tag Selector === */}
            <TagSelector
              availableTags={availableTags}
              selectedTags={selectedTags}
              onSelectTag={handleSelectTag}
              onDeselectTag={handleDeselectTag}
            />

            {/* === Submit Button === */}
            <button
              type="submit"
              className="btn btn-success w-100"
              disabled={
                isLoading || prompt.length === 0 || selectedTags.length === 0
              }
            >
              {isLoading ? (
                <>
                  <span
                    className="spinner-border spinner-border-sm"
                    role="status"
                    aria-hidden="true"
                  ></span>
                  Generating...
                </>
              ) : (
                "Generate"
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
