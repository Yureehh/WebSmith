import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Compass } from "lucide-react";
import { useMemo, useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { CockpitMetrics } from "../components/CockpitMetrics";
import { LeadDetail } from "../components/LeadDetail";
import { LeadFilters } from "../components/LeadFilters";
import { LeadTable } from "../components/LeadTable";
import { LeadTabs } from "../components/LeadTabs";
import { MapPanel } from "../components/MapPanel";
import { SearchControls } from "../components/SearchControls";
import { api } from "../lib/api";
import { defaultExcludedActivities } from "../lib/activityOptions";
import {
  archiveStatuses,
  type AttributeFilter,
  type LeadView,
  matchesLeadFilters,
  workflowStatuses
} from "../lib/leadFilters";
import type { SearchRun } from "../lib/types";

const searchSchema = z.object({
  location_query: z.string().min(2),
  name_query: z.string().optional(),
  radius_km: z.coerce.number().min(0).max(50),
  search_depth: z.enum(["fast", "balanced", "deep"])
});

type SearchForm = z.infer<typeof searchSchema>;

function addUniqueNormalized(
  value: string,
  setItems: (updater: (current: string[]) => string[]) => void,
  clearInput: () => void
) {
  const normalized = value.trim().toLowerCase();
  if (!normalized) return;
  setItems((current) => (current.includes(normalized) ? current : [...current, normalized]));
  clearInput();
}

export function Home() {
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [leadView, setLeadView] = useState<LeadView>("discovered");
  const [currentSearchIds, setCurrentSearchIds] = useState<number[] | null>(null);
  const [currentSearchRun, setCurrentSearchRun] = useState<SearchRun | null>(null);
  const [includedActivities, setIncludedActivities] = useState<string[]>([]);
  const [excludedActivities, setExcludedActivities] = useState<string[]>(defaultExcludedActivities);
  const [includeInput, setIncludeInput] = useState("");
  const [excludeInput, setExcludeInput] = useState("");
  const [leadTextFilter, setLeadTextFilter] = useState("");
  const [leadActivityInput, setLeadActivityInput] = useState("");
  const [leadActivityFilters, setLeadActivityFilters] = useState<string[]>([]);
  const [leadAttributeFilter, setLeadAttributeFilter] = useState<AttributeFilter>("all");
  const queryClient = useQueryClient();
  const businessesQuery = useQuery({ queryKey: ["businesses"], queryFn: api.businesses });
  const { register, handleSubmit, watch } = useForm<SearchForm>({
    defaultValues: {
      location_query: "Forlì",
      name_query: "",
      radius_km: 3,
      search_depth: "balanced"
    }
  });
  const radiusValue = watch("radius_km");
  const searchMutation = useMutation({
    mutationFn: api.search,
    onSuccess: async (data) => {
      await queryClient.invalidateQueries({ queryKey: ["businesses"] });
      setCurrentSearchIds(data.businesses.map((business) => business.id));
      setCurrentSearchRun(data.search_run);
      setLeadView("new");
    }
  });
  const businesses = useMemo(() => businessesQuery.data ?? [], [businessesQuery.data]);
  const currentSearchIdSet = useMemo(
    () => (currentSearchIds ? new Set(currentSearchIds) : null),
    [currentSearchIds]
  );
  const trackedBusinesses = currentSearchIdSet
    ? businesses.filter((business) => currentSearchIdSet.has(business.id))
    : businesses;
  const discoveredBusinesses = businesses.filter(
    (business) => (business.lead_profile?.status ?? "discovered") === "discovered"
  );
  const workflowBusinesses = businesses.filter((business) =>
    workflowStatuses.includes(business.lead_profile?.status ?? "discovered")
  );
  const archivedBusinesses = businesses.filter((business) =>
    archiveStatuses.includes(business.lead_profile?.status ?? "discovered")
  );
  const filteredDiscoveredBusinesses = discoveredBusinesses.filter((business) =>
    matchesLeadFilters(business, leadTextFilter, leadActivityFilters, leadAttributeFilter)
  );
  const filteredWorkflowBusinesses = workflowBusinesses.filter((business) =>
    matchesLeadFilters(business, leadTextFilter, leadActivityFilters, leadAttributeFilter)
  );
  const filteredArchivedBusinesses = archivedBusinesses.filter((business) =>
    matchesLeadFilters(business, leadTextFilter, leadActivityFilters, leadAttributeFilter)
  );
  const newBusinesses = trackedBusinesses.filter(
    (business) => !archiveStatuses.includes(business.lead_profile?.status ?? "discovered")
  );
  const visibleBusinesses =
    leadView === "new"
      ? newBusinesses
      : leadView === "discovered"
        ? filteredDiscoveredBusinesses
        : leadView === "active"
          ? filteredWorkflowBusinesses
          : filteredArchivedBusinesses;
  const activeBacklogCount =
    leadView === "discovered"
      ? discoveredBusinesses.length
      : leadView === "active"
        ? workflowBusinesses.length
        : archivedBusinesses.length;
  const readyCount = businesses.filter((business) =>
    ["draft_ready", "externally_imported", "email_drafted"].includes(
      business.lead_profile?.status ?? "discovered"
    )
  ).length;
  const openTalksCount = businesses.filter((business) =>
    ["contacted", "replied", "follow_up_needed", "proposal_sent"].includes(
      business.lead_profile?.status ?? "discovered"
    )
  ).length;
  const leadTabs = [
    { id: "new", label: "New", count: newBusinesses.length },
    { id: "discovered", label: "Backlog", count: discoveredBusinesses.length },
    { id: "active", label: "Active", count: workflowBusinesses.length },
    { id: "archive", label: "Archive", count: archivedBusinesses.length }
  ] as const;
  const selected = useMemo(
    () => visibleBusinesses.find((business) => business.id === selectedId) ?? null,
    [selectedId, visibleBusinesses]
  );

  const addIncluded = (activity: string) => {
    const normalized = activity.trim().toLowerCase();
    if (!normalized) return;
    setExcludedActivities((current) => current.filter((item) => item !== normalized));
    addUniqueNormalized(normalized, setIncludedActivities, () => setIncludeInput(""));
  };
  const addExcluded = (activity: string) => {
    const normalized = activity.trim().toLowerCase();
    if (!normalized) return;
    setIncludedActivities((current) => current.filter((item) => item !== normalized));
    addUniqueNormalized(normalized, setExcludedActivities, () => setExcludeInput(""));
  };
  const addLeadActivityFilter = (activity: string) => {
    addUniqueNormalized(activity, setLeadActivityFilters, () => setLeadActivityInput(""));
  };
  const onSubmit = (values: SearchForm) => {
    const parsed = searchSchema.parse(values);
    searchMutation.mutate({
      ...parsed,
      name_query: parsed.name_query?.trim() || undefined,
      categories: includedActivities,
      excluded_categories: excludedActivities,
      market_types: [],
      keywords: includedActivities.join(", ")
    });
  };

  return (
    <main className="min-h-screen bg-[linear-gradient(180deg,#f8fbff_0%,#eef8fb_44%,#e8f1f6_100%)]">
      <header className="border-b border-cyan-950/10 bg-white/78 shadow-[0_18px_60px_rgb(15_23_42/0.06)] backdrop-blur-xl">
        <div className="mx-auto flex max-w-[1480px] flex-col gap-4 px-5 py-6 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="mb-1 flex items-center gap-2 text-xs font-black uppercase text-moss">
              <Compass size={14} /> Local growth cockpit
            </p>
            <h1 className="text-5xl font-black tracking-tight text-ink">WebSmith</h1>
            <p className="mt-2 max-w-2xl text-base leading-relaxed text-ink/62">
              Search local businesses, enrich context, prepare website workspaces, and manage outreach manually.
            </p>
          </div>
          <a
            className="inline-flex min-h-11 items-center justify-center rounded-md border border-ink/10 bg-white/70 px-4 py-2 text-sm font-bold text-moss shadow-sm transition hover:border-moss/30 hover:bg-white"
            href="/settings"
          >
            Provider settings
          </a>
        </div>
      </header>

      <div className="mx-auto grid max-w-[1480px] gap-8 px-5 py-8 2xl:grid-cols-[minmax(0,1.7fr)_minmax(390px,0.9fr)]">
        <section className="space-y-7">
          <SearchControls
            activeCount={workflowBusinesses.length}
            addExcluded={addExcluded}
            addIncluded={addIncluded}
            excludeInput={excludeInput}
            excludedActivities={excludedActivities}
            handleSubmit={handleSubmit}
            includeInput={includeInput}
            includedActivities={includedActivities}
            isSearching={searchMutation.isPending}
            onSubmit={onSubmit}
            radiusValue={radiusValue}
            register={register}
            removeExcluded={(activity) =>
              setExcludedActivities((current) => current.filter((item) => item !== activity))
            }
            removeIncluded={(activity) =>
              setIncludedActivities((current) => current.filter((item) => item !== activity))
            }
            searchError={searchMutation.error}
            setExcludeInput={setExcludeInput}
            setIncludeInput={setIncludeInput}
          />

          <CockpitMetrics
            currentSearchRun={currentSearchRun}
            newBusinessCount={newBusinesses.length}
            openTalksCount={openTalksCount}
            readyCount={readyCount}
          />

          <LeadTabs activeView={leadView} setActiveView={setLeadView} tabs={leadTabs} />

          {leadView !== "new" ? (
            <LeadFilters
              activityFilters={leadActivityFilters}
              activityInput={leadActivityInput}
              addActivityFilter={addLeadActivityFilter}
              attributeFilter={leadAttributeFilter}
              removeActivityFilter={(activity) =>
                setLeadActivityFilters((current) => current.filter((item) => item !== activity))
              }
              setActivityInput={setLeadActivityInput}
              setAttributeFilter={setLeadAttributeFilter}
              setTextFilter={setLeadTextFilter}
              shownCount={visibleBusinesses.length}
              textFilter={leadTextFilter}
              totalCount={activeBacklogCount}
            />
          ) : null}

          <div className="grid gap-6 lg:grid-cols-[1.08fr_1fr]">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <h2 className="text-sm font-semibold text-ink">Discovery map</h2>
                <span className="text-xs text-ink/50">{visibleBusinesses.length} leads shown</span>
              </div>
              <MapPanel
                businesses={visibleBusinesses}
                searchRun={currentSearchRun}
                selectedId={selected?.id ?? null}
                onSelect={setSelectedId}
              />
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <h2 className="text-sm font-semibold text-ink">Lead queue</h2>
                <span className="text-xs text-ink/50">Click a row to work it</span>
              </div>
              <LeadTable
                businesses={visibleBusinesses}
                emptyMode={leadView}
                selectedId={selected?.id ?? null}
                onSelect={setSelectedId}
              />
            </div>
          </div>
        </section>

        <section className="space-y-6 2xl:pt-1">
          <LeadDetail business={selected} />
        </section>
      </div>
    </main>
  );
}
