import { ListFilter } from "lucide-react";

import { activityOptions } from "../lib/activityOptions";
import type { AttributeFilter } from "../lib/leadFilters";

type Props = {
  activityInput: string;
  activityFilters: string[];
  attributeFilter: AttributeFilter;
  shownCount: number;
  totalCount: number;
  textFilter: string;
  addActivityFilter: (activity: string) => void;
  removeActivityFilter: (activity: string) => void;
  setActivityInput: (value: string) => void;
  setAttributeFilter: (value: AttributeFilter) => void;
  setTextFilter: (value: string) => void;
};

export function LeadFilters({
  activityFilters,
  activityInput,
  addActivityFilter,
  attributeFilter,
  removeActivityFilter,
  setActivityInput,
  setAttributeFilter,
  setTextFilter,
  shownCount,
  textFilter,
  totalCount
}: Props) {
  return (
    <section className="rounded-lg border border-white/70 bg-white/88 p-4 shadow-[0_14px_45px_rgb(24_32_31/0.07)]">
      <div className="flex flex-col gap-1 md:flex-row md:items-end md:justify-between">
        <p className="flex items-center gap-2 text-sm font-black text-ink">
          <ListFilter size={15} /> FILTERS
        </p>
        <span className="text-xs font-bold text-ink/45">
          {shownCount}/{totalCount} shown
        </span>
      </div>

      <div className="mt-3 grid gap-3 lg:grid-cols-[minmax(220px,1fr)_minmax(220px,1fr)_180px]">
        <label className="grid gap-1.5 text-sm font-medium text-ink">
          NAME / CITY / CATEGORY
          <input
            className="min-h-10 rounded-md border border-ink/12 bg-white px-3 text-sm outline-none focus:border-moss focus:ring-4 focus:ring-moss/12"
            onChange={(event) => setTextFilter(event.target.value)}
            placeholder="Forlì, centro, bar, business name..."
            value={textFilter}
          />
        </label>

        <div className="grid gap-1.5 text-sm font-medium text-ink">
          ACTIVITY TYPE
          <input
            className="min-h-10 min-w-0 flex-1 rounded-md border border-ink/12 bg-white px-3 text-sm outline-none focus:border-moss focus:ring-4 focus:ring-moss/12"
            list="activity-options"
            onBlur={() => addActivityFilter(activityInput)}
            onChange={(event) => setActivityInput(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                event.preventDefault();
                addActivityFilter(activityInput);
              }
            }}
            placeholder="Type activity and press Enter..."
            value={activityInput}
          />
          <datalist id="activity-options">
            {activityOptions.map((activity) => (
              <option key={activity} value={activity} />
            ))}
          </datalist>
        </div>

        <label className="grid gap-1.5 text-sm font-medium text-ink">
          WEBSITE / CONTACT
          <select
            className="min-h-10 rounded-md border border-ink/12 bg-white px-3 text-sm outline-none focus:border-moss focus:ring-4 focus:ring-moss/12"
            onChange={(event) => setAttributeFilter(event.target.value as AttributeFilter)}
            value={attributeFilter}
          >
            <option value="all">All</option>
            <option value="has_website">Has website</option>
            <option value="no_website">No website</option>
            <option value="has_contact">Has contact</option>
            <option value="no_contact">No contact</option>
          </select>
        </label>
      </div>

      {activityFilters.length > 0 ? (
        <div className="mt-3 flex flex-wrap gap-2">
          {activityFilters.map((activity) => (
            <button
              className="rounded-md bg-moss px-2.5 py-1.5 text-xs font-black text-white"
              key={activity}
              onClick={() => removeActivityFilter(activity)}
              type="button"
            >
              {activity} x
            </button>
          ))}
        </div>
      ) : null}
    </section>
  );
}
