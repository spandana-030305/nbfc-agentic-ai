"use client";

import { signIn } from "next-auth/react";
import { useEffect } from "react";

export default function LoginPage() {
  useEffect(() => {
    signIn("google", { callbackUrl: "/chatbot" });
  }, []);

  return (
    <div className="flex h-screen items-center justify-center">
      <p>Redirecting to Google login…</p>
    </div>
  );
}