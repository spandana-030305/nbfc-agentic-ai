"use client";

import { useEffect, useRef, useState } from "react";

export default function Home() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [typing, setTyping] = useState(false);
  const fileInputRef = useRef(null);
  const chatEndRef = useRef(null);

  // Smooth scroll to bottom
  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages, typing]);

  // Send text message to API
  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");

    setTyping(true);

    const res = await fetch("/api/chat", {
      method: "POST",
      body: JSON.stringify({ message: input }),
    });

    const data = await res.json();

    setTyping(false);
    setMessages((prev) => [...prev, { role: "bot", content: data.reply }]);
  };

  // File upload handler
  const uploadFile = async (file) => {
    const form = new FormData();
    form.append("file", file);

    const userMessage = {
      role: "user",
      content: `📎 Uploaded: ${file.name}`,
    };
    setMessages((prev) => [...prev, userMessage]);
    setTyping(true);

    const res = await fetch("/api/chat", {
      method: "POST",
      body: form,
    });

    const data = await res.json();
    setTyping(false);

    setMessages((prev) => [...prev, { role: "bot", content: data.reply }]);
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
          maxWidth: "480px",
          background: "white",
          borderRadius: "25px",
          padding: "25px",
          boxShadow: "0 8px 30px rgba(0,0,0,0.15)",
          display: "flex",
          flexDirection: "column",
          height: "80vh",
        }}
      >
        {/* Header */}
        <h2
          style={{
            fontSize: "22px",
            fontWeight: "700",
            marginBottom: "4px",
            color: "#222",
          }}
        >
          NBFC Chatbot
        </h2>
        <p style={{ color: "#666", marginBottom: "15px" }}>We’re online…</p>

        {/* Chat Window */}
        <div
          style={{
            flexGrow: 1,
            overflowY: "auto",
            paddingRight: "10px",
          }}
        >
          {messages.map((msg, index) => (
            <div
              key={index}
              style={{
                display: "flex",
                marginBottom: "15px",
                justifyContent:
                  msg.role === "user" ? "flex-end" : "flex-start",
              }}
            >
              {/* Avatar */}
              {msg.role === "bot" && (
                <div
                  style={{
                    width: "35px",
                    height: "35px",
                    borderRadius: "50%",
                    background: "#e9e9ff",
                    marginRight: "10px",
                  }}
                />
              )}

              <div
                style={{
                  maxWidth: "70%",
                  background:
                    msg.role === "user" ? "#9b4dff" : "#f3f3f3",
                  color: msg.role === "user" ? "white" : "#333",
                  padding: "12px 16px",
                  borderRadius: "18px",
                  fontSize: "15px",
                }}
              >
                {msg.content}
              </div>

              {msg.role === "user" && (
                <div
                  style={{
                    width: "35px",
                    height: "35px",
                    borderRadius: "50%",
                    background: "#d6b4ff",
                    marginLeft: "10px",
                  }}
                />
              )}
            </div>
          ))}

          {/* Typing animation */}
          {typing && (
            <div
              style={{
                display: "flex",
                alignItems: "center",
                marginBottom: "10px",
              }}
            >
              <div
                style={{
                  width: "35px",
                  height: "35px",
                  borderRadius: "50%",
                  background: "#e9e9ff",
                  marginRight: "10px",
                }}
              ></div>

              <div
                className="typing"
                style={{
                  background: "#f3f3f3",
                  padding: "10px 16px",
                  borderRadius: "16px",
                }}
              >
                <span className="dot"></span>
                <span className="dot"></span>
                <span className="dot"></span>
              </div>

              <style>{`
                .typing {
                  display: flex;
                  gap: 4px;
                }
                .dot {
                  width: 8px;
                  height: 8px;
                  background: #bbb;
                  border-radius: 50%;
                  animation: blink 1.4s infinite both;
                }
                .dot:nth-child(2) {
                  animation-delay: 0.2s;
                }
                .dot:nth-child(3) {
                  animation-delay: 0.4s;
                }
                @keyframes blink {
                  0% { opacity: .2; }
                  20% { opacity: 1; }
                  100% { opacity: .2; }
                }
              `}</style>
            </div>
          )}

          <div ref={chatEndRef}></div>
        </div>

        {/* Input Area */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            marginTop: "10px",
          }}
        >
          {/* File Upload Button */}
          <button
            onClick={() => fileInputRef.current.click()}
            style={{
              background: "#eee",
              border: "none",
              width: "45px",
              height: "45px",
              borderRadius: "50%",
              marginRight: "10px",
              fontSize: "20px",
              cursor: "pointer",
            }}
          >
            📎
          </button>
          <input
            type="file"
            ref={fileInputRef}
            style={{ display: "none" }}
            onChange={(e) => uploadFile(e.target.files[0])}
          />

          {/* Text Input */}
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Enter message"
            style={{
              flexGrow: 1,
              border: "1px solid #ddd",
              padding: "12px 15px",
              borderRadius: "25px",
              outline: "none",
              fontSize: "15px",
            }}
          />

          {/* Send Button */}
          <button
            onClick={sendMessage}
            style={{
              background: "#9b4dff",
              border: "none",
              width: "45px",
              height: "45px",
              borderRadius: "50%",
              marginLeft: "10px",
              cursor: "pointer",
              fontSize: "20px",
              color: "white",
            }}
          >
            ✈️
          </button>
        </div>
      </div>
    </div>
  );
}









