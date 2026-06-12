import { ExternalLink, FileCode2, FolderKanban, Globe2, MapPin, Phone, Sparkles, UserRound } from "lucide-react";

import type { Business } from "../lib/types";
import { LeadActions } from "./LeadActions";

function prettyStatus(status: string) {
  return status.replaceAll("_", " ");
}

function hasContact(business: Business) {
  return Boolean(business.phone || business.email || business.contacts.length > 0);
}

function marketLabel(value: string | undefined) {
  if (value === "b2c") return "B2C";
  if (value === "b2b") return "B2B";
  if (value === "both") return "B2C + B2B";
  return "Unknown";
}

function evidenceClass(found: boolean) {
  return found
    ? "rounded-md bg-moss/10 px-2.5 py-1.5 text-xs font-black text-moss"
    : "rounded-md bg-copper/10 px-2.5 py-1.5 text-xs font-black text-copper";
}

export function LeadDetail({ business }: { business: Business | null }) {
  if (!business) {
    return (
      <aside className="flex h-full min-h-[620px] items-center justify-center rounded-lg border border-dashed border-ink/15 bg-white/82 p-8 text-center shadow-[0_18px_60px_rgb(24_32_31/0.07)]">
        <div>
          <div className="mx-auto mb-4 flex size-14 items-center justify-center rounded-md bg-moss/10 text-moss">
            <Sparkles size={24} />
          </div>
          <p className="text-xl font-black text-ink">Pick a lead to work</p>
          <p className="mt-2 max-w-sm text-sm text-ink/60">
            Select a row or marker to see evidence, workspace status, and available actions.
          </p>
        </div>
      </aside>
    );
  }

  const profile = business.lead_profile;
  const status = profile?.status ?? "discovered";
  const blocked = status === "do_not_contact" || Boolean(profile?.do_not_contact_reason);
  const latestProject = business.website_projects?.[0] ?? null;
  const contactFound = hasContact(business);
  const officialCandidates = business.source_documents.filter(
    (source) => source.source_type === "official_website_candidate"
  );
  const conflictWarning = officialCandidates.find(
    (source) =>
      typeof source.extracted_json?.conflict_warning === "string" &&
      source.extracted_json.conflict_warning
  )?.extracted_json.conflict_warning as string | undefined;

  return (
    <aside className="space-y-4 rounded-lg border border-white/70 bg-white/90 p-4 shadow-[0_22px_70px_rgb(24_32_31/0.09)] backdrop-blur">
      <section className="rounded-lg border border-ink/10 bg-[linear-gradient(135deg,#ffffff_0%,#f4f8f4_100%)] p-5">
        <div className="flex items-start justify-between gap-3">
          <div>
            <p className="text-xs font-black uppercase text-moss">Selected lead</p>
            <h2 className="mt-1 text-3xl font-black leading-tight tracking-tight text-ink">
              {business.name}
            </h2>
          </div>
          <span className="rounded-md bg-ink px-3 py-1.5 text-xs font-black capitalize text-white">
            {prettyStatus(status)}
          </span>
        </div>

        <div className="mt-4 space-y-2 text-sm font-medium text-ink/65">
          <p className="flex items-center gap-2">
            <MapPin size={15} /> {business.formatted_address ?? "Address unknown"}
          </p>
          <p className="flex items-center gap-2">
            <Globe2 size={15} />
            {business.website_url ? (
              <a className="font-black text-moss hover:underline" href={business.website_url} rel="noreferrer" target="_blank">
                Existing website <ExternalLink className="inline" size={12} />
              </a>
            ) : (
              <span className="font-black text-copper">No website found yet</span>
            )}
          </p>
          <p className="flex items-center gap-2">
            <Phone size={15} />{" "}
            {contactFound ? (
              <span className="font-black text-moss">
                {business.phone ?? business.email ?? "Contact captured"}
              </span>
            ) : (
              <span className="font-black text-copper">No public contact captured yet</span>
            )}
          </p>
        </div>

        <div className="mt-4 flex flex-wrap gap-2">
          <span className={evidenceClass(Boolean(business.website_url))}>
            {business.website_url ? "Website found" : "Website missing"}
          </span>
          <span className={evidenceClass(contactFound)}>
            {contactFound ? "Contact found" : "Contact missing"}
          </span>
          <span className="rounded-md bg-ink/10 px-2.5 py-1.5 text-xs font-black uppercase text-ink">
            {marketLabel(profile?.market_type)}
          </span>
          <span className="rounded-md bg-white/85 px-2.5 py-1.5 text-xs font-black uppercase text-ink/55">
            {business.discovery_source}
          </span>
          <span className="rounded-md bg-white/85 px-2.5 py-1.5 text-xs font-black text-ink/55">
            {business.source_documents.length} sources
          </span>
        </div>
      </section>

      {blocked ? (
        <div className="rounded-lg border border-copper/25 bg-copper/10 p-3 text-sm font-semibold text-copper">
          Do not recontact: {profile?.do_not_contact_reason ?? "manual block is active"}.
        </div>
      ) : null}

      {conflictWarning || officialCandidates.length > 1 ? (
        <div className="rounded-lg border border-copper/25 bg-copper/10 p-3 text-sm text-copper">
          <p className="font-black">Website needs confirmation</p>
          <p className="mt-1 font-medium">
            {conflictWarning ?? `${officialCandidates.length} official website candidates found.`}
          </p>
        </div>
      ) : null}

      <LeadActions business={business} />

      <section className="rounded-lg border border-ink/10 bg-white p-4 shadow-sm">
        <h3 className="flex items-center gap-2 text-sm font-black text-ink">
          <FolderKanban size={15} /> Website project
        </h3>
        {latestProject ? (
          <div className="mt-3 space-y-2 text-sm text-ink/70">
            <p>
              <span className="font-semibold text-ink">Status:</span> {latestProject.status}
            </p>
            {latestProject.repo_path ? (
              <p className="break-all">
                <span className="font-semibold text-ink">Workspace:</span> {latestProject.repo_path}
              </p>
            ) : null}
            {latestProject.preview_url ? (
              <a className="inline-flex items-center gap-1 font-semibold text-moss hover:underline" href={latestProject.preview_url} rel="noreferrer" target="_blank">
                Preview <ExternalLink size={12} />
              </a>
            ) : null}
            <p className="rounded-md bg-cloud p-3 text-xs">
              <FileCode2 className="mr-1 inline" size={13} /> Start from `BUILD_BRIEF.md`.
            </p>
          </div>
        ) : (
          <p className="mt-2 text-sm text-ink/60">
            Generate a compact builder workspace when this lead is worth a proposal.
          </p>
        )}
      </section>

      <section className="rounded-lg border border-ink/10 bg-white p-4 shadow-sm">
        <h3 className="flex items-center gap-2 text-sm font-black text-ink">
          <Sparkles size={15} /> Lead notes
        </h3>
        <div className="mt-2 space-y-2 text-sm leading-relaxed text-ink/70">
          <p>{profile?.opportunity_summary ?? "Run enrichment to create a summary."}</p>
          {profile?.recommended_angle ? <p>{profile.recommended_angle}</p> : null}
          {profile?.audience_notes ? <p>{profile.audience_notes}</p> : null}
        </div>
      </section>

      {business.contacts.length > 0 ? (
        <section className="space-y-2">
          <h3 className="flex items-center gap-2 text-sm font-black text-ink">
            <UserRound size={15} /> Contacts
          </h3>
          {business.contacts.map((contact) => (
            <div key={contact.id} className="rounded-lg border border-ink/10 bg-cloud/60 p-3 text-sm">
              <p className="font-semibold text-ink">{contact.name ?? contact.email ?? "Business contact"}</p>
              <p className="text-ink/60">{contact.role ?? contact.contact_type}</p>
              <p className="text-xs text-ink/50">Confidence: {contact.confidence}</p>
            </div>
          ))}
        </section>
      ) : null}

      <section className="space-y-2">
        <h3 className="text-sm font-black text-ink">Source evidence</h3>
        <div className="max-h-44 space-y-2 overflow-auto text-xs text-ink/70">
          {business.source_documents.length === 0 ? (
            <div className="rounded-lg border border-dashed border-ink/15 bg-white p-3 text-ink/50">
              No sources yet. Run enrichment to capture URLs and evidence.
            </div>
          ) : (
            business.source_documents.map((source) => (
              <div key={source.id} className="rounded-lg border border-ink/10 bg-white p-2">
                <p className="font-semibold text-ink">{source.title ?? source.source_type}</p>
                <p className="truncate">{source.source_url ?? "No URL"}</p>
                <p>{source.source_type} · {source.confidence ?? "unknown"}</p>
              </div>
            ))
          )}
        </div>
      </section>
    </aside>
  );
}
