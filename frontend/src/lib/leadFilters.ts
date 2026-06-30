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

const readyStatuses = ["draft_ready", "externally_imported", "email_drafted"];
const talkStatuses = ["contacted", "replied", "follow_up_needed", "proposal_sent"];

function statusOf(business: Business) {
  return business.lead_profile?.status ?? "discovered";
}

export type LeadBuckets = {
  discovered: Business[];
  workflow: Business[];
  archived: Business[];
  newBusinesses: Business[];
  visible: Business[];
  activeBacklogCount: number;
  readyCount: number;
  openTalksCount: number;
  counts: { new: number; discovered: number; active: number; archive: number };
};

/** Derives every lead list/count the cockpit needs from the raw business set. */
export function deriveLeadBuckets(
  businesses: Business[],
  currentSearchIdSet: Set<number> | null,
  leadView: LeadView,
  textFilter: string,
  activityFilters: string[],
  attributeFilter: AttributeFilter
): LeadBuckets {
  const matches = (business: Business) =>
    matchesLeadFilters(business, textFilter, activityFilters, attributeFilter);

  const tracked = currentSearchIdSet
    ? businesses.filter((business) => currentSearchIdSet.has(business.id))
    : businesses;
  const discovered = businesses.filter((business) => statusOf(business) === "discovered");
  const workflow = businesses.filter((business) => workflowStatuses.includes(statusOf(business)));
  const archived = businesses.filter((business) => archiveStatuses.includes(statusOf(business)));
  const newBusinesses = tracked.filter(
    (business) => !archiveStatuses.includes(statusOf(business))
  );

  const visible =
    leadView === "new"
      ? newBusinesses
      : leadView === "discovered"
        ? discovered.filter(matches)
        : leadView === "active"
          ? workflow.filter(matches)
          : archived.filter(matches);

  const activeBacklogCount =
    leadView === "discovered"
      ? discovered.length
      : leadView === "active"
        ? workflow.length
        : archived.length;

  return {
    discovered,
    workflow,
    archived,
    newBusinesses,
    visible,
    activeBacklogCount,
    readyCount: businesses.filter((business) => readyStatuses.includes(statusOf(business))).length,
    openTalksCount: businesses.filter((business) => talkStatuses.includes(statusOf(business))).length,
    counts: {
      new: newBusinesses.length,
      discovered: discovered.length,
      active: workflow.length,
      archive: archived.length
    }
  };
}
