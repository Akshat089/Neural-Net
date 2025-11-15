"use server";

import { NextRequest, NextResponse } from "next/server";
import prisma from "@/prismaClient";
import { getCurrentUser } from "../../auth/lib";
const { decryptSecret } = require("@/lib/xCrypto");

const OAUTH_TOKEN_URL = "https://api.x.com/2/oauth2/token";
const POST_TWEET_URL = "https://api.x.com/2/tweets";

function ensureXCredentialDelegate() {
  const delegate = (prisma as any).xCredential;
  if (!delegate?.findUnique) {
    throw new Error(
      "XCredential model missing in Prisma client. Run `npx prisma generate` so encrypted keys stay outside the user table."
    );
  }
  return delegate as typeof prisma.xCredential;
}

async function getAuthedUser(req: NextRequest) {
  const token = req.cookies.get("auth_token")?.value;
  if (!token) return null;
  return getCurrentUser(token);
}

export async function POST(req: NextRequest) {
  try {
    const user = await getAuthedUser(req);
    if (!user) {
      return NextResponse.json({ error: "Not authenticated" }, { status: 401 });
    }

    const body = await req.json();
    const { text } = body;

    if (!text || typeof text !== "string") {
      return NextResponse.json({ error: "Tweet text is required." }, { status: 400 });
    }

    if (text.length > 280) {
      return NextResponse.json(
        { error: "Tweet text must be 280 characters or fewer." },
        { status: 400 }
      );
    }

    const xCredential = ensureXCredentialDelegate();

    const credentials = await xCredential.findUnique({
      where: { userId: user.id },
      select: { apiKeyEncrypted: true, apiSecretEncrypted: true },
    });

    if (!credentials) {
      return NextResponse.json(
        { error: "X API credentials not found for this user." },
        { status: 400 }
      );
    }

    const apiKey = decryptSecret(credentials.apiKeyEncrypted);
    const apiSecret = decryptSecret(credentials.apiSecretEncrypted);

    const oauthResponse = await fetch(OAUTH_TOKEN_URL, {
      method: "POST",
      headers: {
        Authorization:
          "Basic " + Buffer.from(`${apiKey}:${apiSecret}`).toString("base64"),
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: "grant_type=client_credentials",
    });

    if (!oauthResponse.ok) {
      const errText = await oauthResponse.text();
      return NextResponse.json(
        { error: "Failed to obtain X access token", details: errText },
        { status: oauthResponse.status }
      );
    }

    const { access_token } = await oauthResponse.json();

    const tweetResponse = await fetch(POST_TWEET_URL, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${access_token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ text }),
    });

    const tweetPayload = await tweetResponse.json();

    if (!tweetResponse.ok) {
      return NextResponse.json(
        { error: "Failed to post tweet", details: tweetPayload },
        { status: tweetResponse.status }
      );
    }

    return NextResponse.json({ status: "posted", response: tweetPayload });
  } catch (err: any) {
    console.error("Error posting to X", err);
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
