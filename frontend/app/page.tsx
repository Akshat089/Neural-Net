"use client";
import React, { useState } from "react";
// Import your styles
import "./styles/homepage.css";
import "bootstrap/dist/css/bootstrap.min.css";

// Import the new components from the correct location
import LoginForm from "./components/auth/LoginForm";
import SignUpForm from "./components/auth/SignUpForm";

export default function HomePage() {
  const [activeTab, setActiveTab] = useState("login");
  const [message, setMessage] = useState("");

  return (
    <div className="login-page">
      <div className="home-container">
        <h1 className="text-center text-primary mb-4">
          Creative Automation AI
        </h1>

        <ul className="nav nav-tabs justify-content-center">
          <li className="nav-item">
            <button
              className={`nav-link ${activeTab === "login" ? "active" : ""}`}
              onClick={() => {
                setActiveTab("login");
                setMessage(""); // Clear message on tab switch
              }}
            >
              Sign In
            </button>
          </li>
          <li className="nav-item">
            <button
              className={`nav-link ${activeTab === "signup" ? "active" : ""}`}
              onClick={() => {
                setActiveTab("signup");
                setMessage(""); // Clear message on tab switch
              }}
            >
              Sign Up
            </button>
          </li>
        </ul>

        <div
          className="card mt-4 p-4 shadow-sm mx-auto"
          style={{ maxWidth: "600px" }}
        >
          {/* Display the message if it exists */}
          {message && (
            <div
              className={`alert ${
                message.startsWith("✅") ? "alert-success" : "alert-danger"
              }`}
              role="alert"
            >
              {message}
            </div>
          )}

          {/* Conditionally render the correct form component.
            We pass the `setMessage` function as a prop so the 
            child components can set the message.
          */}
          {activeTab === "login" ? (
            <LoginForm setMessage={setMessage} />
          ) : (
            <SignUpForm setMessage={setMessage} />
          )}
        </div>
      </div>
    </div>
  );
}
