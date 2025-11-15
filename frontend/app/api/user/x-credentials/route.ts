"use server";

import { NextRequest, NextResponse } from "next/server";
import prisma from "@/prismaClient";
import { getCurrentUser } from "../../auth/lib";
const { encryptSecret } = require("@/lib/xCrypto");

function ensureXCredentialDelegate() {
  const delegate = (prisma as any).xCredential;
  if (!delegate?.upsert) {
    throw new Error(
      "XCredential model missing in Prisma client. Run `npx prisma generate` to sync the split credential table."
    );
  }
  return delegate as typeof prisma.xCredential;
}

async function getAuthedUser(req: NextRequest) {
  const token = req.cookies.get("auth_token")?.value;
  if (!token) {
    return null;
  }
  return getCurrentUser(token);
}

export async function PUT(req: NextRequest) {
  try {
    const user = await getAuthedUser(req);
    if (!user) {
      return NextResponse.json({ error: "Not authenticated" }, { status: 401 });
    }

    const body = await req.json();
    const { apiKey, apiSecret } = body;

    if (!apiKey || !apiSecret) {
      return NextResponse.json(
        { error: "Both X API key and secret are required." },
        { status: 400 }
      );
    }

    const [encryptedKey, encryptedSecret] = [
      encryptSecret(apiKey.trim()),
      encryptSecret(apiSecret.trim()),
    ];

    const xCredential = ensureXCredentialDelegate();

    await xCredential.upsert({
      where: { userId: user.id },
      update: {
        apiKeyEncrypted: encryptedKey,
        apiSecretEncrypted: encryptedSecret,
      },
      create: {
        userId: user.id,
        apiKeyEncrypted: encryptedKey,
        apiSecretEncrypted: encryptedSecret,
      },
    });

    return NextResponse.json({ hasXCredentials: true });
  } catch (err: any) {
    console.error("Error storing X credentials", err);
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}

export async function DELETE(req: NextRequest) {
  try {
    const user = await getAuthedUser(req);
    if (!user) {
      return NextResponse.json({ error: "Not authenticated" }, { status: 401 });
    }

    const xCredential = ensureXCredentialDelegate();

    await xCredential
      .delete({
        where: { userId: user.id },
      })
      .catch(() => null);

    return NextResponse.json({ hasXCredentials: false });
  } catch (err: any) {
    console.error("Error removing X credentials", err);
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
