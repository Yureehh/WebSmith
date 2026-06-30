import { clsx } from "clsx";

/** Single shimmering placeholder block. */
export function Skeleton({ className }: { className?: string }) {
  return <div className={clsx("animate-pulse rounded-md bg-ink/8", className)} aria-hidden="true" />;
}

/** Placeholder for the lead queue while the businesses query loads. */
export function LeadQueueSkeleton() {
  return (
    <div
      className="max-h-[470px] overflow-hidden rounded-lg border border-white/70 bg-white shadow-[0_16px_50px_rgb(24_32_31/0.07)]"
      role="status"
      aria-label="Loading leads"
    >
      <div className="grid grid-cols-[1fr_auto] border-b border-ink/10 px-4 py-3">
        <Skeleton className="h-3 w-16" />
        <Skeleton className="h-3 w-6" />
      </div>
      <div className="divide-y divide-ink/10">
        {Array.from({ length: 6 }).map((_, index) => (
          <div className="space-y-2 px-4 py-4" key={index}>
            <Skeleton className="h-4 w-1/2" />
            <Skeleton className="h-3 w-3/4" />
            <div className="flex gap-1.5">
              <Skeleton className="h-5 w-16" />
              <Skeleton className="h-5 w-20" />
              <Skeleton className="h-5 w-14" />
            </div>
          </div>
        ))}
      </div>
      <span className="sr-only">Loading leads…</span>
    </div>
  );
}
