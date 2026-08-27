export interface ApiErrorEnvelope {
  error: {
    code: string;
    message: string;
    details: Array<Record<string, unknown>>;
    retryable: boolean;
    trace_id: string;
  };
}

const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function apiRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(new URL(path, baseUrl), {
    ...init,
    credentials: "include",
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!response.ok) {
    const payload = (await response.json()) as ApiErrorEnvelope;
    throw new Error(`${payload.error.code}: ${payload.error.message}`);
  }
  return (await response.json()) as T;
}
