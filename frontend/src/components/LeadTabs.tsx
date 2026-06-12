import type { LeadView } from "../lib/leadFilters";

type Tab = {
  count: number;
  id: LeadView;
  label: string;
};

type Props = {
  activeView: LeadView;
  tabs: readonly Tab[];
  setActiveView: (view: LeadView) => void;
};

export function LeadTabs({ activeView, setActiveView, tabs }: Props) {
  return (
    <section className="rounded-lg border border-white/70 bg-white/88 p-3 shadow-[0_14px_45px_rgb(24_32_31/0.07)]">
      <div className="flex flex-wrap gap-2">
        {tabs.map((tab) => (
          <button
            className={
              activeView === tab.id
                ? "rounded-md bg-ink px-4 py-2 text-sm font-black text-white shadow-sm"
                : "rounded-md border border-ink/10 bg-white px-4 py-2 text-sm font-black text-ink/55 transition hover:border-moss/30 hover:text-moss"
            }
            key={tab.id}
            onClick={() => setActiveView(tab.id)}
            type="button"
          >
            {tab.label}
            <span className={activeView === tab.id ? "ml-2 text-white/70" : "ml-2 text-ink/35"}>
              {tab.count}
            </span>
          </button>
        ))}
      </div>
    </section>
  );
}
