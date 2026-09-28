export const API_URLS = {
  identity: import.meta.env.VITE_IDENTITY_API_URL ?? "http://localhost:8001",
  transport: import.meta.env.VITE_TRANSPORT_API_URL ?? "http://localhost:8002",
  utility: import.meta.env.VITE_UTILITY_API_URL ?? "http://localhost:8003",
  environment:
    import.meta.env.VITE_ENVIRONMENT_API_URL ?? "http://localhost:8004",
  billing: import.meta.env.VITE_BILLING_API_URL ?? "http://localhost:8005",
};

export function getToken() {
  return localStorage.getItem("access_token");
}

export function setToken(token) {
  if (token) {
    localStorage.setItem("access_token", token);
  } else {
    localStorage.removeItem("access_token");
  }
}

export async function apiFetch(baseUrl, path, options = {}) {
  const token = getToken();
  const headers = new Headers(options.headers);

  if (options.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${baseUrl}${path}`, { ...options, headers });
  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    throw new Error(payload?.detail ?? `Ошибка HTTP ${response.status}`);
  }

  if (response.status === 204) {
    return null;
  }
  return response.json();
}
