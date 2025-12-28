"use client";

import { useEffect, useRef, useState } from "react";

type ChatMessage = { role: "user" | "bot"; content: string };

export default function Home() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [typing, setTyping] = useState(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const chatEndRef = useRef<HTMLDivElement | null>(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages, typing]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const currentInput = input;
    setMessages(prev => [...prev, { role: "user", content: currentInput }]);
    setInput("");
    setTyping(true);

    try {
      const res = await fetch("http://127.0.0.1:9000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: currentInput }),
      });

      const data = await res.json();
      setTyping(false);

      setMessages(prev => [
        ...prev,
        { role: "bot", content: data.reply || "⚠ Invalid response from gateway!" },
      ]);
    } catch {
      setTyping(false);
      setMessages(prev => [...prev, { role: "bot", content: "⚠ Gateway not reachable!" }]);
    }
  };

  const uploadFile = async (file: File) => {
    if (!file) return;

    const form = new FormData();
    form.append("file", file);

    setMessages(prev => [...prev, { role: "user", content: `📎 Uploaded: ${file.name}` }]);
    setTyping(true);

    try {
      const res = await fetch("http://127.0.0.1:9000/chat", {
        method: "POST",
        body: form,
      });

      const data = await res.json();
      setTyping(false);

      setMessages(prev => [
        ...prev,
        { role: "bot", content: data.reply || "⚠ File processed, but no reply from gateway!" },
      ]);
    } catch {
      setTyping(false);
      setMessages(prev => [...prev, { role: "bot", content: "⚠ File upload failed!" }]);
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "linear-gradient(135deg, #a56bff, #6b4eff)",
        padding: "40px 20px",
        display: "flex",
        justifyContent: "center",
      }}
    >
      <div
        style={{
          width: "100%",
          maxWidth: "520px",
          background: "white",
          borderRadius: "25px",
          padding: "24px",
          boxShadow: "0 8px 30px rgba(0,0,0,0.15)",
          display: "flex",
          flexDirection: "column",
          height: "80vh",
        }}
      >
        <h2 style={{ fontSize: "22px", fontWeight: 700, marginBottom: 4, color: "#222" }}>
          NBFC Chatbot
        </h2>
        <p style={{ color: "#666", marginBottom: 16 }}>We’re online…</p>

        {/* CHAT AREA */}
        <div
          style={{
            flexGrow: 1,
            overflowY: "auto",
            paddingRight: 4,
            display: "flex",
            flexDirection: "column",
            gap: 12,
          }}
        >
          {messages.map((msg, idx) => {
            const isUser = msg.role === "user";
            return (
              <div
                key={idx}
                style={{
                  display: "flex",
                  justifyContent: isUser ? "flex-end" : "flex-start",
                }}
              >
                {/* Bot avatar on left */}
                {!isUser && (
                  <div
                    style={{
                      width: 32,
                      height: 32,
                      borderRadius: "50%",
                      background: "#e9e9ff",
                      marginRight: 10,
                      alignSelf: "flex-start",
                      flexShrink: 0,
                    }}
                  />
                )}

                {/* Message bubble */}
                <div
                  style={{
                    maxWidth: "75%",
                    background: isUser ? "#9b4dff" : "#f3f3f3",
                    color: isUser ? "#fff" : "#333",
                    padding: "10px 14px",
                    borderRadius: 18,
                    borderBottomRightRadius: isUser ? 4 : 18,
                    borderBottomLeftRadius: isUser ? 18 : 4,
                    fontSize: 15,
                    lineHeight: 1.5,
                    wordBreak: "break-word",
                    whiteSpace: "pre-wrap", // <-- preserves \n from backend
                  }}
                >
                  {msg.content}
                </div>

                {/* User avatar on right */}
                {isUser && (
                  <div
                    style={{
                      width: 32,
                      height: 32,
                      borderRadius: "50%",
                      background: "#d6b4ff",
                      marginLeft: 10,
                      alignSelf: "flex-start",
                      flexShrink: 0,
                    }}
                  />
                )}
              </div>
            );
          })}

          {typing && (
            <div style={{ display: "flex", alignItems: "center" }}>
              <div
                style={{
                  width: 32,
                  height: 32,
                  borderRadius: "50%",
                  background: "#e9e9ff",
                  marginRight: 10,
                  flexShrink: 0,
                }}
              />
              <div
                style={{
                  background: "#f3f3f3",
                  padding: "8px 14px",
                  borderRadius: 16,
                }}
              >
                ...
              </div>
            </div>
          )}

          <div ref={chatEndRef} />
        </div>

        {/* INPUT AREA */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            marginTop: 12,
            gap: 8,
          }}
        >
          <button
            onClick={() => fileInputRef.current?.click()}
            style={{
              background: "#eee",
              border: "none",
              width: 42,
              height: 42,
              borderRadius: "50%",
              fontSize: 20,
              cursor: "pointer",
              flexShrink: 0,
            }}
          >
            📎
          </button>

          <input
            type="file"
            ref={fileInputRef}
            style={{ display: "none" }}
            onChange={(e) => e.target.files && uploadFile(e.target.files[0])}
          />

          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            placeholder="Enter message"
            style={{
              flexGrow: 1,
              border: "1px solid #ddd",
              padding: "12px 15px",
              borderRadius: 25,
              outline: "none",
              fontSize: 15,
            }}
          />

          <button
            onClick={sendMessage}
            style={{
              background: "#9b4dff",
              border: "none",
              width: 42,
              height: 42,
              borderRadius: "50%",
              cursor: "pointer",
              fontSize: 20,
              color: "#fff",
              flexShrink: 0,
            }}
          >
            ✈️
          </button>
        </div>
      </div>
    </div>
  );
}
