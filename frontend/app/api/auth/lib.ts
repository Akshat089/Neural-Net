import prisma from "@/prismaClient";
import jwt from "jsonwebtoken";

const JWT_SECRET = process.env.JWT_SECRET || "dev_secret";

// Fetch current user from JWT token (query by email)
export async function getCurrentUser(token: string) {
  try {
    if (!token) return null;

    const decoded = jwt.verify(token, JWT_SECRET) as { email: string };
    if (!decoded.email) return null;

    const user = await prisma.user.findUnique({
      where: { email: decoded.email },
      select: { id: true, username: true, email: true, createdAt: true },
    });

    if (!user) return null;

    let hasXCredentials = false;
    try {
      const xCredential = await prisma.xCredential.findUnique({
        where: { userId: user.id },
        select: { id: true },
      });
      hasXCredentials = Boolean(xCredential);
    } catch (credentialError) {
      console.warn(
        "XCredential model unavailable in Prisma client. Run `npx prisma generate` so the split credential table is picked up.",
        credentialError
      );
    }

    return {
      ...user,
      hasXCredentials,
    };
  } catch (err) {
    console.error("Error in getCurrentUser:", err);
    return null;
  }
}

// Create JWT token using email
export function createToken(email: string) {
  return jwt.sign({ email }, JWT_SECRET, { expiresIn: "7d" });
}
