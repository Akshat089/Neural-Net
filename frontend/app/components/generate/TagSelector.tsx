"use client";
import React from "react";
import "../../styles/generate.css"; // Import the styles

interface TagSelectorProps {
  availableTags: string[];
  selectedTags: string[];
  onSelectTag: (tag: string) => void;
  onDeselectTag: (tag: string) => void;
}

export default function TagSelector({
  availableTags,
  selectedTags,
  onSelectTag,
  onDeselectTag,
}: TagSelectorProps) {
  // Calculate unselected tags based on the *available* tags
  const unselectedTags = availableTags.filter(
    (tag) => !selectedTags.includes(tag)
  );

  return (
    <div className="mb-3">
      <label className="form-label fw-bold">Select Targets:</label>
      <div className="tag-container p-2 border rounded">
        {/* 1. Render Selected Tags */}
        {selectedTags.map((tag) => (
          <button
            key={tag}
            type="button"
            className="btn btn-primary btn-sm me-2 mb-2 tag-btn"
            onClick={() => onDeselectTag(tag)}
          >
            <span className="deselect-cross">&times;</span>
            {tag}
          </button>
        ))}

        {/* 2. Render Unselected Tags */}
        {unselectedTags.map((tag) => (
          <button
            key={tag}
            type="button"
            className="btn btn-outline-secondary btn-sm me-2 mb-2"
            onClick={() => onSelectTag(tag)}
          >
            {tag}
          </button>
        ))}
      </div>
    </div>
  );
}
