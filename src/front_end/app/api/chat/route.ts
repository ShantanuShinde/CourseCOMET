import { NextResponse } from "next/server";
import axios from "axios";
import * as dotenv from 'dotenv';

dotenv.config();

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
    const backendUrl = process.env.BACKEND_URL;
    if (!backendUrl) {
        throw new Error("BACKEND_URL is not defined in environment variables.");
    }
    const res = await axios.post(backendUrl, 
      { "question": question }, 
      { headers: { "Content-Type": "application/json" } });
    return res.data.response
}
