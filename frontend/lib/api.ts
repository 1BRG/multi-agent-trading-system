import { getAccessToken } from "./auth";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

type ApiRequestOptions = Omit<RequestInit, "body"> & {
  auth?: boolean;
  body?: BodyInit | object | null;
};

export class ApiError extends Error {
  constructor(
      message: string,
      public readonly status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

function isJsonBody(body: ApiRequestOptions["body"]): body is object {
  return (
    body !== null &&
    body !== undefined &&
    typeof body === "object" &&
    !(body instanceof FormData) &&
    !(body instanceof URLSearchParams) &&
    !(body instanceof Blob)
  );
}

async function getErrorMessage(response: Response): Promise<string> {
  try {
    const payload: unknown = await response.json();
    if (
      payload &&
      typeof payload === "object" &&
      "detail" in payload
    ) {
      const detail = (payload as { detail: unknown }).detail;
      if (typeof detail === "string") {
        return detail;
      }
    }

    if (payload && typeof payload === "object") {
      return Object.entries(payload as Record<string, unknown>)
        .map(([field, value]) => {
          if (Array.isArray(value)) {
            return `${field}: ${value.join(", ")}`;
          }

          if (typeof value === "string") {
            return `${field}: ${value}`;
          }

          return `${field}: ${JSON.stringify(value)}`;
        })
        .join("; ");
    }
  } catch {
    return response.statusText;
  }

  return response.statusText;
}

export async function apiRequest<T>(
    path: string,
    options: ApiRequestOptions = {},
): Promise<T> {
  const { auth = true, body, headers: initialHeaders, ...requestOptions } = options;
  const headers = new Headers(initialHeaders);

  let requestBody: BodyInit | undefined;
  if (isJsonBody(body)) {
    headers.set("Content-Type", "application/json");
    requestBody = JSON.stringify(body);
  } else {
    requestBody = body ?? undefined;
  }

  if (auth) {
    const token = getAccessToken();
    if (token) {
      headers.set("Authorization", `Bearer ${token}`);
    }
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...requestOptions,
    body: requestBody,
    headers,
  });

  if (!response.ok) {
    throw new ApiError(await getErrorMessage(response), response.status);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}
