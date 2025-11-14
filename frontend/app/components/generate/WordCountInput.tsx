"use client";
import React from "react";
import { ChevronUp, ChevronDown } from "lucide-react";

interface WordCountInputProps {
  label: string;
  value: number;
  onChange: (value: number) => void;
}

const WordCountInput: React.FC<WordCountInputProps> = ({
  label,
  value,
  onChange,
}) => {
  const handleIncrement = () => onChange(Math.min(1000, value + 50));
  const handleDecrement = () => onChange(Math.max(50, value - 50));

  return (
    <div className="flex items-center justify-between py-2 border-b border-gray-700">
      <label className="text-gray-300">{label}</label>
      <div className="flex items-center space-x-2">
        <span className="text-white font-mono text-lg w-16 text-right">
          {value}
        </span>
        <div className="flex flex-col space-y-1">
          <button
            type="button"
            onClick={handleIncrement}
            className="p-1 bg-gray-700 rounded-md text-white hover:bg-gray-600 transition-colors"
          >
            <ChevronUp className="w-4 h-4" />
          </button>
          <button
            type="button"
            onClick={handleDecrement}
            className="p-1 bg-gray-700 rounded-md text-white hover:bg-gray-600 transition-colors"
          >
            <ChevronDown className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default WordCountInput;
