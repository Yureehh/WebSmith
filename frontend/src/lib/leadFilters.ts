import type { Business } from "./types";

export type LeadView = "new" | "discovered" | "active" | "archive";

export type AttributeFilter = "all" | "has_website" | "no_website" | "has_contact" | "no_contact";

export const workflowStatuses = [
  "enriched",
  "qualified",
  "creating_website",
  "draft_ready",
  "externally_imported",
  "email_drafted",
  "contacted",
  "replied",
  "follow_up_needed",
  "proposal_sent"
];

export const archiveStatuses = ["won", "lost", "archived", "do_not_contact"];

export function hasContact(business: Business) {
  return Boolean(business.phone || business.email || business.contacts.length > 0);
}

export function matchesLeadFilters(
  business: Business,
  textFilter: string,
  activityFilters: string[],
  attributeFilter: AttributeFilter
) {
  const textNeedle = textFilter.trim().toLowerCase();
  const searchableText = [
    business.name,
    business.formatted_address,
    business.primary_category,
    business.discovery_source,
    ...(business.categories_json ?? [])
  ]
    .filter(Boolean)
    .join(" ")
    .toLowerCase();
  const matchesText = !textNeedle || searchableText.includes(textNeedle);
  const categories = new Set(
    [business.primary_category, ...(business.categories_json ?? [])]
      .filter(Boolean)
      .map((value) => String(value).toLowerCase())
  );
  const matchesActivity =
    activityFilters.length === 0 || activityFilters.some((activity) => categories.has(activity));
  const contactFound = hasContact(business);
  const matchesAttribute =
    attributeFilter === "all" ||
    (attributeFilter === "has_website" && Boolean(business.website_url)) ||
    (attributeFilter === "no_website" && !business.website_url) ||
    (attributeFilter === "has_contact" && contactFound) ||
    (attributeFilter === "no_contact" && !contactFound);
  return matchesText && matchesActivity && matchesAttribute;
}
