import { getServerSession } from "next-auth";
import { authOptions } from "../api/auth/[...nextauth]/route";
import { redirect } from "next/navigation";
import Chatbot from "../../chatbot/chatbot";

export default async function ChatbotPage() {
  const session = await getServerSession(authOptions);

  if (!session) {
    redirect("/login");
  }

  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <div className="p-4 border-b">
        <h1 className="text-xl font-semibold">
          Welcome, {session.user?.name}
        </h1>
      </div>

      {/* Chatbot UI */}
      <div className="flex-1 overflow-hidden">
        <Chatbot />
      </div>
    </div>
  );
}