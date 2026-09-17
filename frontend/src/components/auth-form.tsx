"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";
import type { z } from "zod";

import { ApiError, type User } from "@/lib/api";
import { meKey } from "@/lib/hooks";

type Field = { name: string; label: string; type?: string; autoComplete?: string };

type Props<S extends z.ZodType> = {
  title: string;
  submitLabel: string;
  fields: Field[];
  schema: S;
  action: (values: z.infer<S>) => Promise<User>;
  footer: React.ReactNode;
};

export function AuthForm<S extends z.ZodType>({
  title,
  submitLabel,
  fields,
  schema,
  action,
  footer,
}: Props<S>) {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [errors, setErrors] = useState<Record<string, string>>({});

  const mutation = useMutation({
    mutationFn: action,
    onSuccess: (user) => {
      queryClient.setQueryData(meKey, user);
      router.push("/");
    },
  });

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const raw = Object.fromEntries(new FormData(event.currentTarget));
    const parsed = schema.safeParse(raw);
    if (!parsed.success) {
      const next: Record<string, string> = {};
      for (const issue of parsed.error.issues) {
        const key = String(issue.path[0] ?? "form");
        next[key] ??= issue.message;
      }
      setErrors(next);
      return;
    }
    setErrors({});
    mutation.mutate(parsed.data);
  }

  const serverError =
    mutation.error instanceof ApiError ? mutation.error.detail : mutation.error?.message;

  return (
    <div className="mx-auto w-full max-w-sm space-y-6">
      <h1 className="text-2xl font-semibold">{title}</h1>
      <form onSubmit={onSubmit} className="space-y-4" noValidate>
        {fields.map((field) => (
          <label key={field.name} className="block space-y-1 text-sm">
            <span className="text-muted">{field.label}</span>
            <input
              name={field.name}
              type={field.type ?? "text"}
              autoComplete={field.autoComplete}
              className="w-full rounded-md border border-border bg-surface px-3 py-2 outline-none focus:border-accent"
            />
            {errors[field.name] && <span className="block text-danger">{errors[field.name]}</span>}
          </label>
        ))}
        {serverError && <p className="text-sm text-danger">{serverError}</p>}
        <button
          type="submit"
          disabled={mutation.isPending}
          className="w-full rounded-md bg-accent py-2 font-medium text-accent-foreground hover:opacity-90 disabled:opacity-60"
        >
          {mutation.isPending ? "…" : submitLabel}
        </button>
      </form>
      <p className="text-sm text-muted">{footer}</p>
    </div>
  );
}
