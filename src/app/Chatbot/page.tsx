import { getServerSession } from "next-auth/next";
import { authOptions } from "../api/auth/[...nextauth]/route";
import { redirect } from "next/navigation";

export default async function ChatbotPage() {
  const session = await getServerSession(authOptions);

  if (!session) {
    redirect("/login"); // force login
  }

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold">Welcome, {session.user?.name}</h1>
      <p>Your chatbot goes here.</p>
    </div>
  );
}



