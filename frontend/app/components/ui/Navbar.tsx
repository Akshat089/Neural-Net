"use client";
import React from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

export default function Navbar() {
  const router = useRouter();
  const pathname = usePathname(); // Gets the current route

  const handleSignOut = () => {
    router.push("/"); // Redirect to login page
  };

  // Helper to show which page is active
  const isActive = (path: string) => pathname === path;

  return (
    // 1. Added "sticky-top" to make the navbar stick
    <nav className="navbar navbar-expand navbar-dark bg-dark sticky-top">
      <div className="container-fluid">
        <Link href="/dashboard" className="navbar-brand">
          AI Agent System
        </Link>

        {/* Links are now always visible and aligned to the right */}
        <ul className="navbar-nav ms-auto d-flex flex-row align-items-center">
          <li className="nav-item me-3">
            <Link
              href="/generate"
              className={`nav-link ${isActive("/generate") ? "active" : ""}`}
            >
              Generator
            </Link>
          </li>
          <li className="nav-item me-3">
            <Link
              href="/dashboard"
              className={`nav-link ${isActive("/dashboard") ? "active" : ""}`}
            >
              History
            </Link>
          </li>
          <li className="nav-item me-3">
            <Link
              href="/profile"
              className={`nav-link ${isActive("/profile") ? "active" : ""}`}
            >
              Profile
            </Link>
          </li>
          <li className="nav-item">
            <button onClick={handleSignOut} className="btn btn-outline-danger">
              Sign Out
            </button>
          </li>
        </ul>
      </div>
    </nav>
  );
}
