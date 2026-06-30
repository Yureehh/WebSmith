import { useMutation, useQueryClient } from "@tanstack/react-query";
import { CheckCircle2, MessageSquareReply, Upload } from "lucide-react";
import { useMemo, useState } from "react";
import toast from "react-hot-toast";

import { api } from "../lib/api";
import {
  buildCloseActions,
  buildPrimaryActions,
  buildSecondaryActions,
  isJobResult,
  type LeadAction,
  nextStepCopy,
  readableStatus
} from "../lib/leadActions";
import type { Business } from "../lib/types";
import { Button } from "./Button";
import { Modal } from "./Modal";

export function LeadActions({ business }: { business: Business }) {
  const queryClient = useQueryClient();
  const [replyModal, setReplyModal] = useState<"reply-draft" | "reply-log" | null>(null);
  const [replyText, setReplyText] = useState("");
  const [importModal, setImportModal] = useState(false);
  const [importPath, setImportPath] = useState("");
  const status = business.lead_profile?.status ?? "discovered";
  const blocked =
    status === "do_not_contact" || Boolean(business.lead_profile?.do_not_contact_reason);
  const primaryActions = useMemo(() => buildPrimaryActions(status, blocked), [blocked, status]);
  const secondaryActions = useMemo(() => buildSecondaryActions(status, blocked), [blocked, status]);
  const closeActions = useMemo(() => buildCloseActions(status, blocked), [blocked, status]);

  const mutation = useMutation({
    mutationFn: async ({ run }: { action: LeadAction; run: () => Promise<unknown> }) => {
      const data = await run();
      if (isJobResult(data) && data.status === "failed") {
        throw new Error(data.error || `${data.type} failed.`);
      }
      return data;
    },
    onSuccess: async (data, variables) => {
      const action = variables.action;
      if (isJobResult(data) && data.result_json?.repo_path) {
        toast.success(`Workspace ready: ${String(data.result_json.repo_path)}`);
      } else if (isJobResult(data) && data.result_json?.status) {
        toast.success(`${action.label} completed: ${String(data.result_json.status)}.`);
      } else {
        toast.success(`${action.label} completed.`);
      }
      await queryClient.invalidateQueries({ queryKey: ["businesses"] });
      await queryClient.invalidateQueries({ queryKey: ["business", business.id] });
    },
    onError: (error) => {
      const message = (error as Error).message;
      toast.error(
        message.includes("not reachable")
          ? "Backend is not running. Start it with `make dev-backend`, then retry."
          : message || "Action failed. Please try again."
      );
    }
  });
  const runningActionLabel = mutation.variables?.action.label;

  const runAction = (action: LeadAction) => {
    if (action.modal === "reply-draft" || action.modal === "reply-log") {
      setReplyText("");
      setReplyModal(action.modal);
      return;
    }
    if (action.modal === "import") {
      setImportPath("");
      setImportModal(true);
      return;
    }
    mutation.mutate({ action, run: () => action.run(business.id) });
  };

  const submitReply = () => {
    if (!replyText.trim() || !replyModal) return;
    const action: LeadAction = {
      label: replyModal === "reply-draft" ? "Paste answer + draft reply" : "I received answer",
      help: "",
      icon: MessageSquareReply,
      run: (id) => api.receivedAnswer(id, replyModal === "reply-draft", replyText.trim())
    };
    mutation.mutate({ action, run: () => action.run(business.id) });
    setReplyModal(null);
    setReplyText("");
  };

  const submitImport = () => {
    if (!importPath.trim()) return;
    const cleanPath = importPath.trim();
    const action: LeadAction = {
      label: "Import website",
      help: "",
      icon: Upload,
      run: (id) =>
        api.importWebsite(id, {
          project_name: "External website import",
          repo_path: cleanPath,
          preview_url: cleanPath.startsWith("http") ? cleanPath : undefined,
          notes: "Imported from an external website-building tool."
        })
    };
    mutation.mutate({ action, run: () => action.run(business.id) });
    setImportModal(false);
    setImportPath("");
  };

  const renderAction = (action: LeadAction) => (
    <Button
      className="h-auto min-h-[72px] flex-1 flex-col items-start justify-center gap-1 text-left"
      disabled={mutation.isPending}
      key={action.label}
      onClick={() => runAction(action)}
      variant={action.variant}
    >
      <span className="flex items-center gap-2 text-sm font-black">
        <action.icon size={16} /> {action.label}
      </span>
      <span className="text-xs font-normal leading-snug opacity-65">{action.help}</span>
    </Button>
  );

  return (
    <section className="space-y-3">
      <div className="rounded-lg border border-ink/10 bg-[linear-gradient(135deg,#f7faf7,#eef4ef)] p-4 shadow-sm">
        <p className="flex items-center gap-2 text-xs font-black uppercase text-moss">
          <CheckCircle2 size={14} /> Current step: {readableStatus(status)}
        </p>
        <p className="mt-1 text-sm text-ink/70">{nextStepCopy(status, blocked)}</p>
      </div>

      {primaryActions.length > 0 ? (
        <div className={primaryActions.length === 1 ? "grid gap-2" : "grid gap-2 sm:grid-cols-2"}>
          {primaryActions.map(renderAction)}
        </div>
      ) : null}

      {secondaryActions.length > 0 ? (
        <div>
          <p className="mb-2 text-xs font-black uppercase text-ink/45">Useful side actions</p>
          <div className="grid gap-2 sm:grid-cols-2">{secondaryActions.map(renderAction)}</div>
        </div>
      ) : null}

      {closeActions.length > 0 ? (
        <div>
          <p className="mb-2 text-xs font-black uppercase text-ink/45">Closeout</p>
          <div className="grid gap-2 sm:grid-cols-2">{closeActions.map(renderAction)}</div>
        </div>
      ) : null}

      {mutation.isPending ? (
        <div
          className="fixed inset-0 z-[1000] grid place-items-center bg-ink/30 p-4 backdrop-blur-sm"
          role="dialog"
          aria-modal="true"
          aria-busy="true"
          aria-label={`${runningActionLabel ?? "Working"} in progress`}
        >
          <div
            className="w-full max-w-md rounded-lg border border-white/70 bg-white p-5 text-center shadow-[0_24px_80px_rgb(15_23_42/0.22)]"
            aria-live="polite"
          >
            <div
              className="mx-auto mb-4 size-10 animate-spin rounded-full border-4 border-cyan-100 border-t-moss"
              aria-hidden="true"
            />
            <p className="text-lg font-black text-ink">{runningActionLabel ?? "Working"}</p>
            <p className="mt-2 text-sm leading-relaxed text-ink/60">
              {runningActionLabel === "Enrich" || runningActionLabel === "Enrich again"
                ? "Collecting source context. This can take a moment."
                : "Processing action."}
            </p>
          </div>
        </div>
      ) : null}

      {replyModal ? (
        <Modal
          title={replyModal === "reply-draft" ? "Paste answer and draft reply" : "Log received answer"}
          onClose={() => setReplyModal(null)}
        >
          <p className="text-sm font-black text-ink">
            {replyModal === "reply-draft" ? "Paste answer + draft reply" : "I received answer"}
          </p>
          <textarea
            aria-label="Client answer text"
            className="mt-2 min-h-28 w-full resize-y rounded-md border border-ink/15 p-3 text-sm outline-none focus:border-moss focus:ring-4 focus:ring-moss/12"
            onChange={(event) => setReplyText(event.target.value)}
            placeholder="Paste the latest client answer here..."
            value={replyText}
          />
          <div className="mt-2 flex gap-2">
            <Button disabled={!replyText.trim() || mutation.isPending} onClick={submitReply} variant="primary">
              Save reply
            </Button>
            <Button onClick={() => setReplyModal(null)} variant="quiet">
              Cancel
            </Button>
          </div>
        </Modal>
      ) : null}

      {importModal ? (
        <Modal title="Import website" onClose={() => setImportModal(false)}>
          <p className="text-sm font-black text-ink">Import website</p>
          <p className="mt-1 text-xs text-ink/60">
            Paste a local `site/` folder, zip path, or preview URL.
          </p>
          <input
            aria-label="Website path or URL"
            className="mt-2 min-h-11 w-full rounded-md border border-ink/15 px-3 text-sm outline-none focus:border-moss focus:ring-4 focus:ring-moss/12"
            onChange={(event) => setImportPath(event.target.value)}
            placeholder="/Users/.../website-projects/12-name/site"
            value={importPath}
          />
          <div className="mt-2 flex gap-2">
            <Button disabled={!importPath.trim() || mutation.isPending} onClick={submitImport} variant="primary">
              Attach website
            </Button>
            <Button onClick={() => setImportModal(false)} variant="quiet">
              Cancel
            </Button>
          </div>
        </Modal>
      ) : null}
    </section>
  );
}
