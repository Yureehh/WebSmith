import { ChevronRight, CircleDot, Inbox, Mail, Sparkles } from "lucide-react";

import type { Business } from "../lib/types";
import { formatMarketType, prettyStatus, statusToneFor } from "../lib/statusTones";

type Props = {
  businesses: Business[];
  emptyMode?: "new" | "discovered" | "active" | "archive";
  selectedId: number | null;
  onSelect: (id: number) => void;
};

function nextCue(status: string) {
  if (status === "discovered") return "Enrich next";
  if (status === "enriched" || status === "qualified") return "Website next";
  if (status === "draft_ready" || status === "externally_imported") return "Draft email";
  if (status === "email_drafted") return "Send manually";
  if (status === "contacted") return "Wait / reply";
  if (status === "follow_up_needed") return "Follow up";
  if (status === "replied") return "Continue";
  return "Closed";
}

function hasContact(business: Business) {
  return Boolean(business.phone || business.email || business.contacts.length > 0);
}

export function LeadTable({ businesses, emptyMode = "active", selectedId, onSelect }: Props) {
  if (businesses.length === 0) {
    return (
      <div className="flex min-h-[470px] items-center justify-center rounded-lg border border-dashed border-ink/15 bg-white/80 p-6 text-center shadow-[0_16px_50px_rgb(24_32_31/0.06)]">
        <div>
          <div className="mx-auto mb-3 flex size-12 items-center justify-center rounded-md bg-moss/10 text-moss">
            <Inbox size={22} />
          </div>
          <p className="text-lg font-black text-ink">
            {emptyMode === "archive"
              ? "Archive is empty"
              : emptyMode === "new"
                ? "No new leads in this search"
                : "No leads here yet"}
          </p>
          <p className="mt-2 max-w-sm text-sm text-ink/55">
            {emptyMode === "archive"
              ? "Won, lost, archived, and do-not-contact leads will appear here."
              : emptyMode === "new"
                ? "Everything found in this area is already known. Try a wider radius or different filters."
                : "Search a location, then use filters to narrow this list."}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-h-[470px] overflow-auto rounded-lg border border-white/70 bg-white shadow-[0_16px_50px_rgb(24_32_31/0.07)]">
      <div className="sticky top-0 z-10 grid grid-cols-[1fr_auto] border-b border-ink/10 bg-white/95 px-4 py-3 text-xs font-black uppercase text-ink/45 backdrop-blur">
        <span>Queue</span>
        <span>{businesses.length}</span>
      </div>
      <div className="divide-y divide-ink/10">
        {businesses.map((business) => {
          const status = business.lead_profile?.status ?? "discovered";
          const selected = selectedId === business.id;
          const contactFound = hasContact(business);
          const websiteFound = Boolean(business.website_url);
          const marketType = business.lead_profile?.market_type ?? "unknown";
          return (
            <button
              className={
                selected
                  ? "grid w-full grid-cols-[1fr_auto] gap-3 bg-[linear-gradient(90deg,rgba(61,92,77,0.14),rgba(255,255,255,0.8))] px-4 py-4 text-left"
                  : "grid w-full grid-cols-[1fr_auto] gap-3 px-4 py-4 text-left transition hover:bg-cloud/80"
              }
              key={business.id}
              onClick={() => onSelect(business.id)}
            >
              <span className="min-w-0">
                <span className="flex items-center gap-2">
                  {status === "discovered" ? <CircleDot size={14} /> : null}
                  {status === "enriched" ? <Sparkles size={14} /> : null}
                  {status === "email_drafted" || status === "contacted" ? <Mail size={14} /> : null}
                  <span className="truncate font-black text-ink">{business.name}</span>
                </span>
                <span className="mt-1 block truncate text-xs text-ink/55">
                  {[business.primary_category, business.formatted_address].filter(Boolean).join(" · ") ||
                    "local business"}
                </span>
                <span className="mt-2 flex flex-wrap gap-1.5">
                  <span
                    className={`rounded-md px-2 py-1 text-[11px] font-black capitalize ${statusToneFor(status)}`}
                    title={`Status: ${prettyStatus(status)}`}
                  >
                    {prettyStatus(status)}
                  </span>
                  <span className="rounded-md bg-cloud px-2 py-1 text-[11px] font-bold text-ink/55">
                    {nextCue(status)}
                  </span>
                  <span
                    className={
                      marketType === "unknown"
                        ? "rounded-md bg-ink/5 px-2 py-1 text-[11px] font-black uppercase text-ink/45"
                        : "rounded-md bg-ink/10 px-2 py-1 text-[11px] font-black uppercase text-ink"
                    }
                  >
                    {formatMarketType(marketType)}
                  </span>
                  <span
                    className={
                      websiteFound
                        ? "rounded-md bg-moss/10 px-2 py-1 text-[11px] font-black text-moss"
                        : "rounded-md bg-copper/10 px-2 py-1 text-[11px] font-black text-copper"
                    }
                  >
                    {websiteFound ? "Website" : "No website"}
                  </span>
                  <span
                    className={
                      contactFound
                        ? "rounded-md bg-moss/10 px-2 py-1 text-[11px] font-black text-moss"
                        : "rounded-md bg-copper/10 px-2 py-1 text-[11px] font-black text-copper"
                    }
                  >
                    {contactFound ? "Contact" : "No contact"}
                  </span>
                  <span className="rounded-md bg-ink/5 px-2 py-1 text-[11px] font-bold text-ink/55">
                    {business.discovery_source.toUpperCase()}
                  </span>
                </span>
              </span>
              <span className="flex items-center gap-2 text-xs font-bold text-ink/45">
                {nextCue(status)}
                <ChevronRight size={16} />
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
