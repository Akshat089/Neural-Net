"use client";
import React, { useState, useCallback } from "react";
import InputCard from "../generate/InputCard";
import TextInput from "../generate/TextInput";
import { Lightbulb, Loader2,Download,
  Image as ImageIcon } from "lucide-react";

const IMAGE_ENDPOINT =
  process.env.NEXT_PUBLIC_IMAGE_GENERATION ||
  "https://dd1235--nn-image-imagegenserver-generate-image.modal.run";

interface ImageResult {
  url: string;
  fileKey: string;
  prompt: string;
}

const YoutubeScriptPage: React.FC = () => {
  const [formData, setFormData] = useState({
    channelDescription: "",
    prompt: "",
    subscribers: "",
    videoType: "shortform",
    tone: "",
    audience: "",
    threadId: "e.g. session-abc123",
  });

  const [result, setResult] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [imagePrompt, setImagePrompt] = useState("");
  const [imagePromptLoading, setImagePromptLoading] = useState(false);
  const [imageResult, setImageResult] = useState<ImageResult | null>(null);
  const [imageError, setImageError] = useState<string | null>(null);
  const handleChange = useCallback(
    (key: keyof typeof formData, value: string | number | string[]) => {
      setFormData((prev) => ({ ...prev, [key]: value }));
    },
    []
  );

  const handleSelectionChange = useCallback((selectedNames: string[]) => {
    setFormData((prev) => ({
      ...prev,
      modalities: selectedNames,
    }));
  }, []);

  const autoGenerateImagePrompt = useCallback(async () => {
      setImagePromptLoading(true);
      setImageError(null);
      try {
        const backendUrl = process.env.NEXT_PUBLIC_PYTHON_BACKEND_URL;
        if (!backendUrl) {
          throw new Error("Python backend URL is not configured.");
        }
        const res = await fetch(`${backendUrl}/image-prompt`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            channelDescription: formData.channelDescription,
            prompt: formData.prompt,
            script: result || "",
            tone: formData.tone,
            audience: formData.audience,
          }),
        });
        if (!res.ok) {
          throw new Error(`Prompt helper failed (${res.status})`);
        }
        const data = await res.json();
        const promptText = data.image_prompt || data.prompt;
        if (!promptText) {
          throw new Error("No prompt returned by helper.");
        }
        setImagePrompt(promptText);
      } catch (err: any) {
        console.error("Image prompt helper error:", err);
        setImageError(
          err?.message || "Failed to craft image prompt from your content."
        );
      } finally {
        setImagePromptLoading(false);
      }
    }, [
      formData.channelDescription,
      formData.prompt,
      result,
      formData.tone,
      formData.audience,
    ]);
  
    const generateImageFromPrompt = useCallback(
      async (promptText: string) => {
        if (!promptText.trim()) return null;
  
        try {
          const response = await fetch(IMAGE_ENDPOINT, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ prompt: promptText }),
          });
  
          if (!response.ok) {
            const message = await response.text();
            throw new Error(message || `Image API error (${response.status})`);
          }
  
          const payload = await response.json();
          const fileKey = payload.file_key || payload.fileKey || "";
          const publicUrl = payload.public_url || payload.publicUrl;
  
          if (!publicUrl) {
            throw new Error("Image service did not return a public URL.");
          }
  
          try {
            const saveRes = await fetch("/api/generated-images", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              credentials: "include",
              body: JSON.stringify({
                prompt: promptText,
                fileKey,
                imageUrl: publicUrl,
              }),
            });
  
            if (!saveRes.ok && saveRes.status === 401) {
              setImageError("Login required to store generated images.");
            }
          } catch (saveErr) {
            console.error("Failed to save generated image:", saveErr);
          }
  
          return {
            url: publicUrl,
            fileKey,
            prompt: promptText,
          };
        } catch (err: any) {
          console.error("Image generation error:", err);
          setImageError(
            err?.message || "Failed to generate image from the provided prompt."
          );
          return null;
        }
      },
      []
    );

  const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  setLoading(true);
  setResult(null);
  setImageError(null);
  setImageResult(null);

  try {
    // 1️⃣ Generate the YouTube script
    const res = await fetch(
      `${process.env.NEXT_PUBLIC_PYTHON_BACKEND_URL}/generate-youtube-script`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      }
    );
    const data = await res.json();
    const generatedScript = data.generated_script;
    setResult(generatedScript);

    // 2️⃣ Generate image prompt based on generated script
    if (generatedScript) {
      setImagePromptLoading(true);
      const promptRes = await fetch(`${process.env.NEXT_PUBLIC_PYTHON_BACKEND_URL}/image-prompt`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          channelDescription: formData.channelDescription,
          prompt: formData.prompt,
          script: generatedScript,
          tone: formData.tone,
          audience: formData.audience,
        }),
      });
      const promptData = await promptRes.json();
      const craftedPrompt = promptData.image_prompt || promptData.prompt;
      setImagePrompt(craftedPrompt);

      // 3️⃣ Generate the image from prompt
      const img = await generateImageFromPrompt(craftedPrompt);
      if (img) setImageResult(img);

      setImagePromptLoading(false);
    }
  } catch (err) {
    console.error(err);
    setResult("⚠️ Failed to generate script or image");
    setImagePromptLoading(false);
  } finally {
    setLoading(false);
  }
};


  return (
    <form
      onSubmit={handleSubmit}
      className="p-6 md:p-10 text-white max-w-4xl mx-auto"
    >
      <h1 className="text-3xl font-bold mb-2">
        Dashboard / Youtube Script{" "}
        <span className="text-gray-400 font-normal text-xl">
          /generate_youtube_script
        </span>
      </h1>
      <p className="text-gray-400 mb-8">
        Create a script for youtube videos.
      </p>

      <InputCard title="Channel Description">
        <TextInput
          label="Define your channel persona and tone."
          value={formData.channelDescription}
          onChange={(e) => handleChange("channelDescription", e.target.value)}
        />
      </InputCard>

      <InputCard title="Content">
        <TextInput
          label="Prompt"
          value={formData.prompt}
          onChange={(e) => handleChange("prompt", e.target.value)}
          placeholder="What should the agent write about?"
          isTextArea
        />
      </InputCard>

      <InputCard title="Subscribers">
        <TextInput
          label=""
          value={formData.subscribers}
          onChange={(e) => handleChange("subscribers", e.target.value)}
          placeholder="600k"
        />
      </InputCard>

      <InputCard title="Tone">
        <TextInput
          label=""
          value={formData.tone}
          onChange={(e) => handleChange("tone", e.target.value)}
          placeholder="inquisitive"
        />
      </InputCard>

      <InputCard title="Audience">
        <TextInput
          label=""
          value={formData.audience}
          onChange={(e) => handleChange("audience", e.target.value)}
          placeholder="middle aged men"
        />
      </InputCard>
      
      <InputCard title="Video Type">
        <div className="flex gap-4">
        <label className="flex items-center gap-2">
            <input
                type="radio"
                name="videoType"
                value="longform"
                checked={formData.videoType === "longform"}
                onChange={(e) => handleChange("videoType", e.target.value)}
            />
            Longform
        </label>

        <label className="flex items-center gap-2">
            <input
                type="radio"
                name="videoType"
                value="shortform"
                checked={formData.videoType === "shortform"}
                onChange={(e) => handleChange("videoType", e.target.value)}
            />
            Shortform
            </label>
            </div>
        </InputCard>


      <InputCard title="Thread ID (optional)">
        <TextInput
          label=""
          value={formData.threadId}
          onChange={(e) => handleChange("threadId", e.target.value)}
          placeholder="e.g. session-abc123"
        />
      </InputCard>

      <InputCard title="Thumbnail Generator">
        <div className="space-y-3">
          <TextInput
            label="Describe the hero image you'd like the SDXL model to create."
            value={imagePrompt}
            onChange={(e) => setImagePrompt(e.target.value)}
            isTextArea
            placeholder="e.g. Ultra-detailed cinematic shot of..."
          />
          <div className="flex flex-wrap items-center gap-3">
            <button
              type="button"
              onClick={autoGenerateImagePrompt}
              disabled={imagePromptLoading || loading}
              className="inline-flex items-center px-4 py-2 rounded-lg bg-amber-500 text-black font-semibold hover:bg-amber-400 transition disabled:opacity-60"
            >
              {imagePromptLoading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Crafting prompt...
                </>
              ) : (
                <>
                  <Lightbulb className="w-4 h-4 mr-2" />
                  Suggest from brief
                </>
              )}
            </button>
            <p className="text-xs text-gray-400">
              The lightbulb uses your brand voice + content brief to craft an SDXL-ready prompt.
            </p>
          </div>
          {imageError && (
            <p className="text-xs text-red-300">{imageError}</p>
          )}
        </div>
      </InputCard>

      <div className="mt-8">
        <button
          type="submit"
          disabled={loading}
          className="w-full md:w-auto px-8 py-3 bg-red-600 text-white font-bold rounded-xl shadow-xl hover:bg-red-700 transition-all duration-300 transform hover:scale-[1.01] focus:outline-none focus:ring-4 focus:ring-red-500/50 flex items-center justify-center"
        >
          <Lightbulb className="w-5 h-5 mr-3" />
          {loading ? "Generating..." : "Youtube Script "}
        </button>
      </div>

      {result && (
        <div className="mt-10 bg-gray-800 p-6 rounded-xl shadow-lg">
          <h2 className="text-xl font-bold mb-3">Generated Youtube Script:</h2>
          <pre className="whitespace-pre-wrap text-gray-200">{result}</pre>
        </div>
      )}
      {imageResult && (
        <div className="mt-8 bg-gray-800 rounded-xl shadow-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-xl font-bold flex items-center gap-2">
                <ImageIcon className="w-5 h-5 text-red-400" />
                Generated Image
              </h3>
              <p className="text-sm text-gray-400">
                Prompt: <span className="text-gray-200">{imageResult.prompt}</span>
              </p>
            </div>
            <a
              href={imageResult.url}
              download
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center px-4 py-2 text-sm font-semibold rounded-lg bg-gray-700 hover:bg-gray-600 transition-colors"
            >
              <Download className="w-4 h-4 mr-2" />
              Download
            </a>
          </div>
          <div className="bg-black/40 rounded-lg overflow-hidden border border-gray-700">
            <img
              src={imageResult.url}
              alt="Generated visual asset"
              className="w-full h-auto object-cover"
            />
          </div>
        </div>
      )}
    </form>
  );
};

export default YoutubeScriptPage;
