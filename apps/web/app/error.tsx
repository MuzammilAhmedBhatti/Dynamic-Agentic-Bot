"use client";

import { ErrorState } from "@/components/error-state";

export default function Error({ reset }: Readonly<{ error: Error & { digest?: string }; reset: () => void }>) {
  return (
    <div className="space-y-4">
      <ErrorState message="The application shell could not be rendered." />
      <button className="rounded-lg bg-[var(--accent)] px-4 py-2 font-medium text-[#052219]" onClick={reset} type="button">Try again</button>
    </div>
  );
}
