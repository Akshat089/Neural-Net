"use client";
import React from "react";

interface TextInputProps {
  label: string;
  value: string;
  onChange: (event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => void;
  placeholder?: string;
  isTextArea?: boolean;
}

const TextInput: React.FC<TextInputProps> = ({
  label,
  value,
  onChange,
  placeholder,
  isTextArea = false,
}) => {
  const InputComponent = isTextArea ? "textarea" : "input";
  return (
    <div className="mb-4">
      <label className="block text-sm font-medium text-gray-300 mb-2">{label}</label>
      <InputComponent
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className={`w-full bg-gray-900 text-white border border-gray-700 rounded-lg p-3 focus:ring-blue-500 focus:border-blue-500 transition-colors ${
          isTextArea ? "min-h-[120px] resize-none" : ""
        }`}
      />
    </div>
  );
};

export default TextInput;
