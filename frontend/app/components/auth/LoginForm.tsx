"use client";
import React, { useState } from "react";
import { useRouter } from "next/navigation";

// Define the props the component will accept (a function to set the message)
interface LoginFormProps {
  setMessage: (message: string) => void;
}

export default function LoginForm({ setMessage }: LoginFormProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const router = useRouter();

  const BACKEND_URL =
    process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:4000";

  const loginHandle = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch(`${BACKEND_URL}/api/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      const data = await res.json();
      if (res.ok) {
        setMessage(`✅ ${data.message}`);
        router.push("/dashboard");
      } else {
        setMessage(`❌ ${data.error}`);
      }
    } catch (err: any) {
      setMessage(`⚠️ Network error: ${err.message}`);
    }
  };

  return (
    <form onSubmit={loginHandle}>
      <h3 className="text-center mb-3">Sign In</h3>
      <div className="mb-3">
        <label className="text-start d-block">Email address</label>
        <input
          type="email"
          className="form-control"
          placeholder="Enter email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
      </div>
      <div className="mb-3">
        <label className="text-start d-block">Password</label>
        <input
          type="password"
          className="form-control"
          placeholder="Enter password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
      </div>
      <button type="submit" className="btn btn-primary w-100">
        Sign In
      </button>
    </form>
  );
}
