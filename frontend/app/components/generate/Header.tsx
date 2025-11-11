"use client";
import React from "react";
import { Menu } from "lucide-react";

interface HeaderProps {
  onToggleSidebar: () => void;
  currentPage: string;
}

const Header: React.FC<HeaderProps> = ({ onToggleSidebar, currentPage }) => {
  const pageTitle = currentPage
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");

  return (
    <header className="fixed top-0 left-0 right-0 z-10 bg-gray-900 border-b border-gray-700/50 p-4 flex items-center justify-between md:hidden">
      <div className="flex items-center">
        <button
          onClick={onToggleSidebar}
          className="text-gray-300 hover:text-white mr-4"
          aria-label="Toggle Sidebar"
        >
          <Menu className="w-6 h-6" />
        </button>
        <h1 className="text-lg font-semibold text-white">{pageTitle}</h1>
      </div>
    </header>
  );
};

export default Header;
