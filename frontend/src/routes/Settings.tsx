import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { CheckCircle2, Globe2, Save, SearchCheck, Sparkles } from "lucide-react";
import { useEffect } from "react";
import { useForm } from "react-hook-form";

import { Button } from "../components/Button";
import { api } from "../lib/api";
import type { ProviderSettings } from "../lib/types";

export function Settings() {
  const queryClient = useQueryClient();
  const settingsQuery = useQuery({ queryKey: ["provider-settings"], queryFn: api.providerSettings });
  const { register, handleSubmit, reset } = useForm<ProviderSettings>({
    defaultValues: { web_search_backup_enabled: false }
  });
  const mutation = useMutation({
    mutationFn: api.updateProviderSettings,
    onSuccess: async () => queryClient.invalidateQueries({ queryKey: ["provider-settings"] })
  });

  useEffect(() => {
    if (settingsQuery.data) reset(settingsQuery.data);
  }, [reset, settingsQuery.data]);

  return (
    <main className="min-h-screen bg-cloud">
      <header className="border-b border-ink/10 bg-white">
        <div className="mx-auto flex max-w-4xl items-center justify-between px-4 py-4">
          <div>
            <h1 className="text-2xl font-bold text-ink">Provider settings</h1>
          </div>
          <a className="rounded-md px-3 py-2 text-sm font-medium text-moss hover:bg-cloud" href="/">
            Back to cockpit
          </a>
        </div>
      </header>
      <form
        className="mx-auto mt-6 grid max-w-4xl gap-4 rounded-lg border border-ink/10 bg-white p-5 shadow-[0_18px_60px_rgb(24_32_31/0.06)]"
        onSubmit={handleSubmit((values) => mutation.mutate(values))}
      >
        <div className="grid gap-3 md:grid-cols-2">
          <div className="rounded-md border border-ink/10 bg-cloud p-4">
            <p className="flex items-center gap-2 text-xs font-black uppercase text-ink/45">
              <SearchCheck size={17} /> Discovery
            </p>
            <p className="mt-2 text-xl font-bold text-ink">OSM / Overpass</p>
          </div>
          <div className="rounded-md border border-ink/10 bg-cloud p-4">
            <p className="flex items-center gap-2 text-xs font-black uppercase text-ink/45">
              <Sparkles size={17} /> AI drafts
            </p>
            <p className="mt-2 text-xl font-bold text-ink">
              {settingsQuery.data?.ai_key_configured ? "OpenAI key connected" : "OpenAI key missing"}
            </p>
          </div>
          <div className="rounded-md border border-ink/10 bg-cloud p-4">
            <p className="flex items-center gap-2 text-xs font-black uppercase text-ink/45">
              <Globe2 size={17} /> Enrich web lookup
            </p>
            <p className="mt-2 text-xl font-bold text-ink">
              {settingsQuery.data?.enrich_web_search_enabled ? "On" : "Off"}
            </p>
            <p className="mt-2 text-xs leading-relaxed text-ink/55">
              Runs only when you click Enrich and the OpenAI key is connected.
            </p>
          </div>
          <div className="rounded-md border border-ink/10 bg-cloud p-4">
            <p className="flex items-center gap-2 text-xs font-black uppercase text-ink/45">
              <CheckCircle2 size={17} /> Overpass
            </p>
            <p className="mt-2 text-xl font-bold text-ink">
              {settingsQuery.data?.overpass_configured ? "Ready" : "Missing URL"}
            </p>
          </div>
          <div className="rounded-md border border-ink/10 bg-cloud p-4">
            <p className="flex items-center gap-2 text-xs font-black uppercase text-ink/45">
              <Globe2 size={17} /> Web search backup
            </p>
            <div className="mt-2 flex items-center justify-between gap-3">
              <p className="text-xl font-bold text-ink">
                {settingsQuery.data?.web_search_backup_enabled ? "On" : "Off"}
              </p>
              <input className="size-5" type="checkbox" {...register("web_search_backup_enabled")} />
            </div>
            <p className="mt-2 text-xs leading-relaxed text-ink/55">
              Uses OpenAI web search to supplement area discovery. It can incur API/tool usage, so
              it stays off by default.
            </p>
          </div>
        </div>
        <p className="text-xs text-ink/45">
          Paid map APIs are not used. Discovery stays OSM-first; selected-lead Enrich can still
          use OpenAI web lookup when your key is connected.
        </p>
        <Button className="w-fit" variant="primary" disabled={mutation.isPending}>
          <Save size={16} /> Save settings
        </Button>
      </form>
    </main>
  );
}
