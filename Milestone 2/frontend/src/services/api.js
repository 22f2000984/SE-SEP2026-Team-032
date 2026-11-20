/* Talks to the backend. Set VITE_API_URL (for example http://localhost:5001) to turn the backend on.
   Without it the app keeps using the sample data in the browser, exactly as before. */
const BASE = String(import.meta.env.VITE_API_URL || '').replace(/\/$/, '');
export const API_ON = BASE !== '';

const TOKEN_KEY = 't32_token';

export function getToken() {
  try { return sessionStorage.getItem(TOKEN_KEY); } catch { return null; }
}
export function setToken(token) {
  try { sessionStorage.setItem(TOKEN_KEY, token); } catch { /* storage blocked */ }
}
export function clearToken() {
  try { sessionStorage.removeItem(TOKEN_KEY); } catch { /* storage blocked */ }
}

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

/* One call to the backend. Returns the JSON, or throws an ApiError whose message is the backend's {"error": "..."} text. */
export async function api(method, path, body) {
  const headers = {};
  const token = getToken();
  if (token) headers.Authorization = 'Bearer ' + token;
  if (body !== undefined) headers['Content-Type'] = 'application/json';

  let response;
  try {
    response = await fetch(BASE + path, { method, headers, body: body === undefined ? undefined : JSON.stringify(body) });
  } catch {
    throw new ApiError('Cannot reach the server. It may be waking up, please try again in a minute.', 0);
  }
  if (response.status === 204) return null;
  let data = null;
  try { data = await response.json(); } catch { /* no JSON body */ }
  if (!response.ok) throw new ApiError((data && data.error) || `The server answered with an error (${response.status}).`, response.status);
  return data;
}
