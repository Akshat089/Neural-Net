"use client";
import React from "react";
import { CheckCircle } from "lucide-react";
import InputCard from "./InputCard";

export interface Modality {
  name: string;
  active: boolean;
}

interface ModalitySelectorProps {
  modalities: Modality[];
  onToggle: (name: string) => void;
}

const ModalitySelector: React.FC<ModalitySelectorProps> = ({ modalities, onToggle }) => (
  <InputCard title="Modalities" description="Select the platform types for your blog assets.">
    <div className="flex flex-wrap gap-3">
      {modalities.map((modality) => (
        <button
          key={modality.name}
          onClick={() => onToggle(modality.name)}
          className={`px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 ${
            modality.active
              ? "bg-red-600 text-white hover:bg-red-700"
              : "bg-gray-600 text-gray-200 hover:bg-gray-500"
          } flex items-center`}
        >
          {modality.active && <CheckCircle className="w-4 h-4 mr-2" />}
          {modality.name}
        </button>
      ))}
    </div>
  </InputCard>
);

export default ModalitySelector;
