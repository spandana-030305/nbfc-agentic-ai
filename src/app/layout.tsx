import type { Metadata } from "next";
import Providers from "./providers";

export const metadata: Metadata = {
  title: "NBFC Chatbot",
  description: "Federated login enabled chatbot",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased">
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}



