"use client";

import { useEffect, useRef, useState } from "react";

export default function Chatbot() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [typing, setTyping] = useState(false);
  const fileInputRef = useRef(null);
  const chatEndRef = useRef(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages, typing]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const currentInput = input;
    setMessages((prev) => [...prev, { role: "user", content: currentInput }]);
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

      setMessages((prev) => [
        ...prev,
        { role: "bot", content: data.reply || "⚠ Invalid response from gateway!" },
      ]);
    } catch {
      setTyping(false);
      setMessages((prev) => [
        ...prev,
        { role: "bot", content: "⚠ Gateway not reachable!" },
      ]);
    }
  };

  const uploadFile = async (file) => {
    if (!file) return;

    const form = new FormData();
    form.append("file", file);

    setMessages((prev) => [
      ...prev,
      { role: "user", content: `📎 Uploaded: ${file.name}` },
    ]);
    setTyping(true);

    try {
      const res = await fetch("http://127.0.0.1:9000/chat", {
        method: "POST",
        body: form,
      });

      const data = await res.json();
      setTyping(false);

      setMessages((prev) => [
        ...prev,
        {
          role: "bot",
          content: data.reply || "⚠ File processed, but no reply from gateway!",
        },
      ]);
    } catch {
      setTyping(false);
      setMessages((prev) => [
        ...prev,
        { role: "bot", content: "⚠ File upload failed!" },
      ]);
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
        <h2 style={{ fontSize: "22px", fontWeight: 700, marginBottom: 4 }}>
          NBFC Chatbot
        </h2>
        <p style={{ color: "#666", marginBottom: 16 }}>We’re online…</p>

        {/* CHAT AREA */}
        <div style={{ flexGrow: 1, overflowY: "auto", marginBottom: 12 }}>
          {messages.map((msg, idx) => (
            <div
              key={idx}
              style={{
                textAlign: msg.role === "user" ? "right" : "left",
                marginBottom: 8,
              }}
            >
              <span
                style={{
                  display: "inline-block",
                  background: msg.role === "user" ? "#9b4dff" : "#eee",
                  color: msg.role === "user" ? "#fff" : "#333",
                  padding: "8px 12px",
                  borderRadius: 12,
                }}
              >
                {msg.content}
              </span>
            </div>
          ))}

          {typing && <p style={{ color: "#999" }}>Bot is typing…</p>}
          <div ref={chatEndRef} />
        </div>

        {/* INPUT */}
        <div style={{ display: "flex", gap: 8 }}>
          <button onClick={() => fileInputRef.current?.click()}>📎</button>
          <input
            type="file"
            ref={fileInputRef}
            style={{ display: "none" }}
            onChange={(e) => uploadFile(e.target.files[0])}
          />
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            placeholder="Enter message"
            style={{ flexGrow: 1 }}
          />
          <button onClick={sendMessage}>Send</button>
        </div>
      </div>
    </div>
  );
}