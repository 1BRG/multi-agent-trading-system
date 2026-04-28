export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function apiRequest<T>(_path: string): Promise<T> {
  throw new Error("TODO: Implement API request helper.");
}
