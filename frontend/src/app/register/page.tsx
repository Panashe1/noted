"use client";

import Link from "next/link";
import { z } from "zod";

import { AuthForm } from "@/components/auth-form";
import { api } from "@/lib/api";

const schema = z.object({
  email: z.email("Enter a valid email address"),
  username: z
    .string()
    .trim()
    .toLowerCase()
    .regex(/^[a-z0-9_]{3,30}$/, "3–30 characters: letters, numbers and underscores"),
  password: z.string().min(8, "At least 8 characters").max(128),
});

export default function RegisterPage() {
  return (
    <AuthForm
      title="Create your account"
      submitLabel="Join Noted"
      schema={schema}
      action={api.register}
      fields={[
        { name: "email", label: "Email", type: "email", autoComplete: "email" },
        { name: "username", label: "Username", autoComplete: "username" },
        { name: "password", label: "Password", type: "password", autoComplete: "new-password" },
      ]}
      footer={
        <>
          Already have an account?{" "}
          <Link href="/login" className="text-accent hover:underline">
            Log in
          </Link>
        </>
      }
    />
  );
}
