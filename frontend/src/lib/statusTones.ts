// Centralized status + market-type presentation helpers (single source of truth).

/** Tailwind classes for a lead status badge. */
export const statusTone: Record<string, string> = {
  discovered: "bg-ink/5 text-ink/65",
  enriched: "bg-moss/10 text-moss",
  qualified: "bg-moss/10 text-moss",
  draft_ready: "bg-copper/10 text-copper",
  externally_imported: "bg-copper/10 text-copper",
  email_drafted: "bg-moss/10 text-moss",
  contacted: "bg-ink text-white",
  replied: "bg-moss text-white",
  follow_up_needed: "bg-copper text-white",
  proposal_sent: "bg-ink text-white",
  won: "bg-moss text-white",
  lost: "bg-ink/70 text-white",
  do_not_contact: "bg-copper text-white",
  archived: "bg-ink/20 text-ink/70"
};

export const statusToneFallback = "bg-cloud text-ink/70";

export function statusToneFor(status: string): string {
  return statusTone[status] ?? statusToneFallback;
}

/** Human-readable status label ("draft ready" from "draft_ready"). */
export function prettyStatus(status: string): string {
  return status.replaceAll("_", " ");
}

/** Marker fill colors for the discovery map, keyed by market type. */
export const marketColorHex: Record<string, string> = {
  b2c: "#0f766e",
  both: "#0891b2",
  b2b: "#2563eb",
  unknown: "#6b7280"
};

export function formatMarketType(marketType: string): string {
  if (marketType === "b2c") return "B2C";
  if (marketType === "b2b") return "B2B";
  if (marketType === "both") return "B2C + B2B";
  return "Unknown";
}
