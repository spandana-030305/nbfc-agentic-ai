import { NextResponse } from "next/server";

export async function POST(request: Request) {
  try {
    const { message } = await request.json();

    if (!message) {
      return NextResponse.json(
        { reply: "Message is required" },
        { status: 400 }
      );
    }

    // Forward request to local FastAPI API Gateway
    const gatewayRes = await fetch("http://127.0.0.1:9000/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });

    const data = await gatewayRes.json();

    if (!gatewayRes.ok) {
      return NextResponse.json(
        { reply: "Gateway error", error: data.detail || "Unknown error" },
        { status: 502 }
      );
    }

    return NextResponse.json({ reply: data.reply });

  } catch (err: any) {
    return NextResponse.json(
      { reply: "Internal server error", error: err.message },
      { status: 500 }
    );
  }
}





