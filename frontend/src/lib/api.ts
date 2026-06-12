import type { Business, ProviderSettings, SearchRun } from "./types";

const jsonHeaders = { "Content-Type": "application/json" };

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(path, init);
  } catch {
    throw new Error("WebSmith API is not reachable. Start the backend on localhost:8000.");
  }
  if (!response.ok) {
    const text = await response.text();
    let message = text || response.statusText;
    try {
      const parsed = JSON.parse(text) as { detail?: unknown; error?: unknown; error_type?: unknown };
      const detail =
        typeof parsed.detail === "string" ? parsed.detail : JSON.stringify(parsed.detail);
      const error = typeof parsed.error === "string" ? parsed.error : JSON.stringify(parsed.error);
      message = [detail, error].filter(Boolean).join(": ") || response.statusText;
    } catch {
      message = text || response.statusText;
    }
    throw new Error(message);
  }
  return response.json() as Promise<T>;
}

export type SearchPayload = {
  location_query: string;
  name_query?: string;
  radius_km: number;
  keywords?: string;
  categories: string[];
  excluded_categories: string[];
  market_types: string[];
  max_results?: number;
  search_depth: "fast" | "balanced" | "deep";
};

export type WebsiteImportPayload = {
  project_name: string;
  repo_path?: string;
  preview_url?: string;
  notes?: string;
};

export const api = {
  businesses: () => request<Business[]>("/api/businesses"),
  business: (id: number) => request<Business>(`/api/businesses/${id}`),
  search: (payload: SearchPayload) =>
    request<{ search_run: SearchRun; businesses: Business[] }>("/api/search-runs", {
      method: "POST",
      headers: jsonHeaders,
      body: JSON.stringify(payload)
    }),
  enrich: (id: number) => request(`/api/businesses/${id}/enrich`, { method: "POST" }),
  generateWebsite: (id: number) =>
    request(`/api/businesses/${id}/generate-website`, { method: "POST" }),
  importWebsite: (
    id: number,
    payload: WebsiteImportPayload = { project_name: "External import", notes: "Imported by user" }
  ) =>
    request(`/api/businesses/${id}/import-website`, {
      method: "POST",
      headers: jsonHeaders,
      body: JSON.stringify(payload)
    }),
  draftOutreach: (id: number) =>
    request(`/api/businesses/${id}/draft-outreach`, {
      method: "POST",
      headers: jsonHeaders,
      body: JSON.stringify({ language: "it" })
    }),
  markEmailSent: (id: number) =>
    request(`/api/businesses/${id}/mark-email-sent`, {
      method: "POST",
      headers: jsonHeaders,
      body: JSON.stringify({ note: "Sent manually from external mail client" })
    }),
  receivedAnswer: (id: number, draftReply = true, message = "Pasted client reply...") =>
    request(`/api/businesses/${id}/received-answer`, {
      method: "POST",
      headers: jsonHeaders,
      body: JSON.stringify({
        message,
        draft_reply: draftReply,
        next_step: "follow_up_needed"
      })
    }),
  followUp: (id: number) =>
    request(`/api/businesses/${id}/follow-up`, {
      method: "POST",
      headers: jsonHeaders,
      body: JSON.stringify({
        next_follow_up_at: new Date(Date.now() + 7 * 86400000).toISOString(),
        note: "Follow up later"
      })
    }),
  doNotContact: (id: number) =>
    request(`/api/businesses/${id}/do-not-contact`, {
      method: "POST",
      headers: jsonHeaders,
      body: JSON.stringify({ reason: "Marked manually in WebSmith" })
    }),
  status: (id: number, status: string) =>
    request(`/api/businesses/${id}/status`, {
      method: "POST",
      headers: jsonHeaders,
      body: JSON.stringify({ status })
    }),
  providerSettings: () => request<ProviderSettings>("/api/settings/providers"),
  updateProviderSettings: (payload: ProviderSettings) =>
    request<ProviderSettings>("/api/settings/providers", {
      method: "PUT",
      headers: jsonHeaders,
      body: JSON.stringify({
        web_search_backup_enabled: payload.web_search_backup_enabled
      })
    })
};
