import { NextResponse } from "next/server";
import axios from "axios";
export async function POST(request: Request) {
  try {
    const { question } = await request.json();
    // Simulate a response
    const response = {
      response: await getResponse(question),
    };
    return NextResponse.json(response);
  } catch (error) {
    console.error("Error processing ask request:", error);
    return NextResponse.json({ error: "Failed to process request" }, { status: 500 });
  }
}

// Placeholder logic — you can replace this with actual call to Python backend
async function getResponse(question: string): Promise<string> {
    const res = await axios.post("http://127.0.0.1:8000/api/ask", 
      { "question": question }, 
      { headers: { "Content-Type": "application/json" } });
    return res.data.response
}
