export function ErrorState({ message }: Readonly<{ message: string }>) {
  return <div role="alert" className="rounded-xl border border-red-400/40 bg-red-500/10 p-4 text-sm text-red-100">{message}</div>;
}
