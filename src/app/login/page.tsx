"use client";

import { signIn } from "next-auth/react";

export default function LoginPage() {
  return (
    <div className="flex flex-col items-center justify-center h-screen bg-white">
      <h1 className="text-2xl font-bold mb-6">Login to continue</h1>
      <button
        onClick={() => signIn("google", { callbackUrl: "/chatbot" })}
        className="px-5 py-3 border rounded-full flex items-center gap-3 hover:bg-gray-100 text-base"
      >
        Continue with Google
      </button>
    </div>
  );
}


