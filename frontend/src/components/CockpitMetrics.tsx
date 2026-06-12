import { MessagesSquare } from "lucide-react";

import type { SearchRun } from "../lib/types";

type Props = {
  currentSearchRun: SearchRun | null;
  newBusinessCount: number;
  openTalksCount: number;
  readyCount: number;
};

export function CockpitMetrics({
  currentSearchRun,
  newBusinessCount,
  openTalksCount,
  readyCount
}: Props) {
  return (
    <div className="grid gap-3 md:grid-cols-3">
      <div className="rounded-lg border border-white/70 bg-white/88 p-4 shadow-[0_14px_45px_rgb(24_32_31/0.07)]">
        <p className="text-xs font-semibold uppercase text-ink/45">New added</p>
        <p className="mt-1 text-3xl font-black text-ink">
          {currentSearchRun?.new_added_count ?? newBusinessCount}
        </p>
        <p className="mt-1 text-xs text-ink/45">
          {currentSearchRun ? `${currentSearchRun.duplicate_skipped_count} known skipped` : "No search yet"}
        </p>
      </div>
      <div className="rounded-lg border border-white/70 bg-white/88 p-4 shadow-[0_14px_45px_rgb(24_32_31/0.07)]">
        <p className="text-xs font-semibold uppercase text-ink/45">Coverage</p>
        <p className="mt-1 text-3xl font-black text-ink">
          {currentSearchRun?.coverage_json.length ?? 0}
        </p>
        <p className="mt-1 text-xs text-ink/45">
          {currentSearchRun
            ? `${currentSearchRun.total_seen_count} seen · ${currentSearchRun.excluded_count} excluded`
            : "tiles searched"}
        </p>
      </div>
      <div className="rounded-lg border border-white/70 bg-[linear-gradient(135deg,#ffffff,#ecfeff)] p-4 shadow-[0_14px_45px_rgb(15_23_42/0.07)]">
        <p className="flex items-center gap-1 text-xs font-semibold uppercase text-ink/45">
          <MessagesSquare size={13} /> Open talks
        </p>
        <p className="mt-1 text-3xl font-black text-moss">{openTalksCount}</p>
        <p className="mt-1 text-xs text-ink/45">{readyCount} website-ready</p>
      </div>
    </div>
  );
}
