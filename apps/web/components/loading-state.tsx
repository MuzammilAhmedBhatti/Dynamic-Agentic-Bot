export function LoadingState({ label = "Loading" }: Readonly<{ label?: string }>) {
  return <p role="status" className="animate-pulse text-sm text-[var(--muted)]">{label}…</p>;
}
