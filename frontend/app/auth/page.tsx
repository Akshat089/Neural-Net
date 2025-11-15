import React, { Suspense } from "react";
import AuthClient from "./AuthClient"; // <-- Import the component you just renamed

// This is now a Server Component, which is what Next.js wants!
export default function Page() {
  return (
    // The <Suspense> boundary is the fix.
    // It tells Next.js: "Render 'Loading...' on the server,
    // and wait for the client to load the AuthClient component."
    <Suspense fallback={<div>Loading...</div>}>
      <AuthClient />
    </Suspense>
  );
}
