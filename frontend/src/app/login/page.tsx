"use client";

import Link from "next/link";
import { z } from "zod";

import { AuthForm } from "@/components/auth-form";
import { api } from "@/lib/api";

const schema = z.object({
  identifier: z.string().trim().min(1, "Enter your email or username"),
  password: z.string().min(1, "Enter your password"),
});

export default function LoginPage() {
  return (
    <AuthForm
      title="Welcome back"
      submitLabel="Log in"
      schema={schema}
      action={api.login}
      fields={[
        { name: "identifier", label: "Email or username", autoComplete: "username" },
        { name: "password", label: "Password", type: "password", autoComplete: "current-password" },
      ]}
      footer={
        <>
          New here?{" "}
          <Link href="/register" className="text-accent hover:underline">
            Create an account
          </Link>
        </>
      }
    />
  );
}
