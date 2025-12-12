"use client";
import { useState } from "react";
import ChatWindow from "@/components/ChatWindow";

export default function Home() {
  const [sessionId] = useState(() => crypto.randomUUID());

  return (
    <main className="flex h-screen justify-center items-center bg-gray-100">
      <ChatWindow sessionId={sessionId} />
    </main>
  );
}
