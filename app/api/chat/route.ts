import { NextResponse } from "next/server";

export async function POST(request) {
  const contentType = request.headers.get("content-type");

  // -------- FILE UPLOAD CASE --------
  if (contentType && contentType.includes("multipart/form-data")) {
    const form = await request.formData();
    const file = form.get("file");

    if (!file) {
      return NextResponse.json({ reply: "No file uploaded!" });
    }

    const filename = file.name;

    // OPTIONAL: read file contents
    // const bytes = await file.arrayBuffer();

    return NextResponse.json({
      reply: `📄 I received your file: **${filename}**. Thanks for uploading!`,
    });
  }

  // -------- TEXT MESSAGE CASE --------
  try {
    const { message } = await request.json();
    const text = message?.toLowerCase() || "";
    let reply = "";

    if (text.includes("hello") || text.includes("hi")) {
      reply = "Hey there! 👋 How can I help you today?";
    } else if (text.includes("how are you")) {
      reply = "I'm doing great! Thanks for asking 😊 What about you?";
    } else if (text.includes("help")) {
      reply = "Sure! Tell me what you need help with 😊";
    } else if (text.includes("your name")) {
      reply = "I'm your NBFC Chatbot Assistant 🤖✨";
    } else if (text.endsWith("?")) {
      reply = "That's an interesting question 🤔 Let me think about it...";
    } else {
      reply = "I see! Tell me more about it.";
    }

    return NextResponse.json({ reply });
  } catch (err) {
    // If request.json() fails → invalid JSON → user sent empty body
    return NextResponse.json({
      reply: "I didn’t understand that. Could you try again?",
    });
  }
}




