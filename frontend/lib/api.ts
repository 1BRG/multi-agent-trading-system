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

function formatErrorValue(value: unknown): string {
  if (Array.isArray(value)) {
    return value.map(formatErrorValue).filter(Boolean).join(", ");
  }

  if (value && typeof value === "object") {
    return Object.entries(value as Record<string, unknown>)
      .map(([field, fieldValue]) => {
        const message = formatErrorValue(fieldValue);
        return message ? `${field}: ${message}` : "";
      })
      .filter(Boolean)
      .join("; ");
  }

  if (typeof value === "string") {
    return value;
  }

  if (value === null || value === undefined) {
    return "";
  }

  return String(value);
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
          const message = formatErrorValue(value);
          return message ? `${field}: ${message}` : "";
        })
        .filter(Boolean)
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

  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...requestOptions,
      body: requestBody,
      headers,
    });
  } catch {
    throw new ApiError(
      "Could not reach the server. Check that the backend is running.",
      0,
    );
  }

  if (!response.ok) {
    throw new ApiError(await getErrorMessage(response), response.status);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}
