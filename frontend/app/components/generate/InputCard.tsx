"use client";
import React from "react";

interface InputCardProps {
  title: string;
  children: React.ReactNode;
  description?: string;
}

const InputCard: React.FC<InputCardProps> = ({ title, children, description }) => (
  <div className="bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-700/50 mb-6">
    <h3 className="text-lg font-semibold text-white mb-1">{title}</h3>
    {description && <p className="text-sm text-gray-400 mb-4">{description}</p>}
    {children}
  </div>
);

export default InputCard;
