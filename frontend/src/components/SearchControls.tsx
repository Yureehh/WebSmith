import { FilterX, Gauge, ListFilter, MapPin, Search, SlidersHorizontal, Target } from "lucide-react";
import type { UseFormHandleSubmit, UseFormRegister } from "react-hook-form";

import { activityOptions } from "../lib/activityOptions";
import { Button } from "./Button";

export type SearchFormValues = {
  location_query: string;
  name_query?: string;
  radius_km: number;
  search_depth: "fast" | "balanced" | "deep";
};

type Props = {
  activeCount: number;
  excludedActivities: string[];
  includeInput: string;
  includedActivities: string[];
  isSearching: boolean;
  radiusValue: number;
  searchError: Error | null;
  excludeInput: string;
  handleSubmit: UseFormHandleSubmit<SearchFormValues>;
  register: UseFormRegister<SearchFormValues>;
  addExcluded: (activity: string) => void;
  addIncluded: (activity: string) => void;
  onClearFilters: () => void;
  onSubmit: (values: SearchFormValues) => void;
  removeExcluded: (activity: string) => void;
  removeIncluded: (activity: string) => void;
  setExcludeInput: (value: string) => void;
  setIncludeInput: (value: string) => void;
};

export function SearchControls({
  activeCount,
  addExcluded,
  addIncluded,
  excludeInput,
  excludedActivities,
  handleSubmit,
  includeInput,
  includedActivities,
  isSearching,
  onClearFilters,
  onSubmit,
  radiusValue,
  register,
  removeExcluded,
  removeIncluded,
  searchError,
  setExcludeInput,
  setIncludeInput
}: Props) {
  const hasFilters =
    includedActivities.length > 0 || excludeInput.length > 0 || includeInput.length > 0;
  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      className="rounded-lg border border-white/80 bg-white/90 p-4 shadow-[0_24px_80px_rgb(15_23_42/0.08)] backdrop-blur"
    >
      <div className="mb-4 flex flex-col gap-2 border-b border-ink/10 pb-4 md:flex-row md:items-center md:justify-between">
        <p className="flex items-center gap-2 text-base font-black text-ink">
          <SlidersHorizontal size={16} /> Search controls
        </p>
        <div className="flex flex-wrap gap-2">
          <div className="rounded-md bg-moss/10 px-3 py-2 text-xs font-black text-moss">
            OSM / Overpass discovery
          </div>
          <div className="rounded-md bg-ink/5 px-3 py-2 text-xs font-black text-ink/60">
            {activeCount} active
          </div>
        </div>
      </div>

      <div className="grid gap-3 lg:grid-cols-[minmax(240px,1.4fr)_minmax(170px,0.9fr)_120px_minmax(160px,0.9fr)]">
        <label className="grid gap-1.5 text-sm font-medium text-ink">
          <span className="flex items-center gap-2 text-xs font-black uppercase tracking-wide text-ink/65">
            <MapPin size={14} /> Location
          </span>
          <input
            className="min-h-12 rounded-md border border-ink/12 bg-white px-3 py-2 text-base font-semibold outline-none transition focus:border-moss focus:ring-4 focus:ring-moss/12"
            placeholder="Forlì, Via delle Torri, quartiere, landmark..."
            {...register("location_query")}
          />
        </label>

        <label className="grid gap-1.5 text-sm font-medium text-ink">
          <span className="flex items-center gap-2 text-xs font-black uppercase tracking-wide text-ink/65">
            <Search size={14} /> Business name
          </span>
          <input
            className="min-h-12 rounded-md border border-ink/12 bg-white px-3 py-2 text-base font-semibold outline-none transition focus:border-moss focus:ring-4 focus:ring-moss/12"
            placeholder="Optional"
            {...register("name_query")}
          />
        </label>

        <label className="grid gap-1.5 text-sm font-medium text-ink">
          <span className="flex items-center gap-2 text-xs font-black uppercase tracking-wide text-ink/65">
            <Target size={14} /> Radius
          </span>
          <div className="flex min-h-12 items-center rounded-md border border-ink/12 bg-white px-3 transition focus-within:border-moss focus-within:ring-4 focus-within:ring-moss/12">
            <input
              className="w-full border-0 bg-transparent py-2 outline-none"
              type="number"
              min="0"
              step="0.5"
              {...register("radius_km")}
            />
            <span className="text-sm text-ink/50">km</span>
          </div>
        </label>

        <label className="grid gap-1.5 text-sm font-medium text-ink">
          <span className="flex items-center gap-2 text-xs font-black uppercase tracking-wide text-ink/65">
            <Gauge size={14} /> Depth
          </span>
          <select
            className="min-h-12 rounded-md border border-ink/12 bg-white px-3 py-2 text-base font-semibold outline-none transition focus:border-moss focus:ring-4 focus:ring-moss/12"
            {...register("search_depth")}
          >
            <option value="fast">Fast — quick scan</option>
            <option value="balanced">Balanced — recommended</option>
            <option value="deep">Deep — exhaustive</option>
          </select>
        </label>

        <div className="grid content-end lg:col-span-4">
          <Button className="min-h-12 w-full px-6 text-base" variant="primary" disabled={isSearching}>
            <Search size={16} /> {isSearching ? "Searching…" : "Search"}
          </Button>
        </div>
      </div>

      <div className="mt-4 grid gap-3 border-t border-ink/10 pt-4 lg:grid-cols-2">
        <div>
          <p className="flex items-center gap-2 text-sm font-black text-ink">
            <ListFilter size={15} /> INCLUDE TYPES
          </p>
          <div className="mt-2 flex flex-wrap gap-2">
            <input
              aria-label="Add an activity type to include in the search"
              className="min-h-10 flex-1 rounded-md border border-ink/12 bg-white px-3 text-sm outline-none focus:border-moss focus:ring-4 focus:ring-moss/12"
              list="activity-options"
              onBlur={() => addIncluded(includeInput)}
              onChange={(event) => setIncludeInput(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  event.preventDefault();
                  addIncluded(includeInput);
                }
              }}
              placeholder="Type activity and press Enter..."
              value={includeInput}
            />
            <datalist id="activity-options">
              {activityOptions.map((activity) => (
                <option key={activity} value={activity} />
              ))}
            </datalist>
          </div>
          <div className="mt-2 flex flex-wrap gap-2">
            {includedActivities.map((activity) => (
              <button
                aria-label={`Remove included type ${activity}`}
                className="rounded-md bg-moss px-2.5 py-1.5 text-xs font-black text-white transition hover:bg-moss/85"
                key={activity}
                onClick={() => removeIncluded(activity)}
                type="button"
              >
                {activity} <span aria-hidden="true">×</span>
              </button>
            ))}
          </div>
        </div>

        <div>
          <p className="flex items-center gap-2 text-sm font-black text-ink">
            <FilterX size={15} /> EXCLUDE TYPES
          </p>
          <div className="mt-2 flex flex-wrap gap-2">
            <input
              aria-label="Add an activity type to exclude from the search"
              className="min-h-10 flex-1 rounded-md border border-ink/12 bg-white px-3 text-sm outline-none focus:border-copper focus:ring-4 focus:ring-copper/12"
              list="activity-options"
              onBlur={() => addExcluded(excludeInput)}
              onChange={(event) => setExcludeInput(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  event.preventDefault();
                  addExcluded(excludeInput);
                }
              }}
              placeholder="Type activity to exclude and press Enter..."
              value={excludeInput}
            />
          </div>
          <div className="mt-2 flex max-h-28 flex-wrap gap-2 overflow-auto rounded-md pr-1">
            {excludedActivities.map((activity) => (
              <button
                aria-label={`Remove excluded type ${activity}`}
                className="rounded-md bg-copper px-2.5 py-1.5 text-xs font-black text-white transition hover:bg-copper/85"
                key={activity}
                onClick={() => removeExcluded(activity)}
                type="button"
              >
                {activity} <span aria-hidden="true">×</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="mt-4 flex items-center justify-between gap-3 text-xs">
        <button
          className="inline-flex items-center gap-1.5 rounded-md px-2.5 py-1.5 font-bold text-ink/55 transition enabled:hover:bg-ink/5 enabled:hover:text-ink disabled:opacity-40"
          disabled={!hasFilters}
          onClick={onClearFilters}
          type="button"
        >
          <FilterX size={13} /> Clear filters
        </button>
        <span className="text-ink/45">Current radius: {radiusValue || 0} km</span>
      </div>
      {searchError ? (
        <div className="mt-4 rounded-md border border-copper/20 bg-copper/10 p-3 text-sm font-semibold text-copper">
          {searchError.message}
        </div>
      ) : null}
    </form>
  );
}
