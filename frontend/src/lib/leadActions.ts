import {
  Archive,
  Ban,
  CalendarClock,
  Download,
  MailCheck,
  MailPlus,
  MessageSquareReply,
  Sparkles,
  Trophy,
  Upload,
  XCircle
} from "lucide-react";

import { api } from "./api";
import type { JobResult } from "./types";

export type LeadAction = {
  label: string;
  help: string;
  icon: typeof Sparkles;
  modal?: "reply-draft" | "reply-log" | "import";
  variant?: "primary" | "secondary" | "danger" | "quiet";
  run: (id: number) => Promise<unknown>;
};

export const terminalStatuses = new Set(["won", "lost", "archived", "do_not_contact"]);
export const contactedStatuses = new Set([
  "contacted",
  "replied",
  "follow_up_needed",
  "proposal_sent"
]);
export const websiteReadyStatuses = new Set([
  "draft_ready",
  "externally_imported",
  "email_drafted"
]);

export function readableStatus(status: string) {
  return status.replaceAll("_", " ");
}

export function buildPrimaryActions(status: string, blocked: boolean): LeadAction[] {
  if (blocked || terminalStatuses.has(status)) return [];

  if (status === "discovered") {
    return [
      {
        label: "Enrich",
        help: "Collect website, contact, and source context.",
        icon: Sparkles,
        variant: "primary",
        run: api.enrich
      }
    ];
  }

  if (status === "enriched" || status === "qualified") {
    return [
      {
        label: "Generate website",
        help: "Create BUILD_BRIEF.md and workspace.",
        icon: Download,
        variant: "primary",
        run: api.generateWebsite
      },
      {
        label: "Import website",
        help: "Attach a site path, URL, or zip.",
        icon: Upload,
        modal: "import",
        run: api.importWebsite
      }
    ];
  }

  if (websiteReadyStatuses.has(status)) {
    return [
      {
        label: "Draft first email",
        help: "Draft only. Nothing is sent.",
        icon: MailPlus,
        variant: "primary",
        run: api.draftOutreach
      },
      ...(status === "email_drafted"
        ? [
            {
              label: "I sent email",
              help: "Record your manual send.",
              icon: MailCheck,
              run: api.markEmailSent
            }
          ]
        : [])
    ];
  }

  if (contactedStatuses.has(status)) {
    return [
      {
        label: "Paste answer + draft reply",
        help: "Save reply and draft response.",
        icon: MessageSquareReply,
        modal: "reply-draft",
        variant: "primary",
        run: api.receivedAnswer
      },
      {
        label: "Follow up later",
        help: "Set a manual reminder.",
        icon: CalendarClock,
        run: api.followUp
      }
    ];
  }

  return [];
}

export function buildSecondaryActions(status: string, blocked: boolean): LeadAction[] {
  if (blocked || terminalStatuses.has(status)) return [];

  if (status === "enriched" || status === "qualified") {
    return [
      {
        label: "Enrich again",
        help: "Refresh source context.",
        icon: Sparkles,
        run: api.enrich
      },
      {
        label: "Follow up later",
        help: "Set a manual reminder.",
        icon: CalendarClock,
        run: api.followUp
      }
    ];
  }

  if (status === "draft_ready" || status === "externally_imported") {
    return [
      {
        label: "Import website",
        help: "Attach updated output.",
        icon: Upload,
        modal: "import",
        run: api.importWebsite
      },
      {
        label: "Follow up later",
        help: "Set a manual reminder.",
        icon: CalendarClock,
        run: api.followUp
      }
    ];
  }

  if (status === "email_drafted") {
    return [
      {
        label: "Follow up later",
        help: "Set a manual reminder.",
        icon: CalendarClock,
        run: api.followUp
      }
    ];
  }

  if (contactedStatuses.has(status)) {
    return [
      {
        label: "I received answer",
        help: "Log reply without draft.",
        icon: MessageSquareReply,
        modal: "reply-log",
        run: api.receivedAnswer
      }
    ];
  }

  return [];
}

export function buildCloseActions(status: string, blocked: boolean): LeadAction[] {
  return [
    ...(contactedStatuses.has(status)
      ? [
          {
            label: "Won",
            help: "Mark converted.",
            icon: Trophy,
            run: (id: number) => api.status(id, "won")
          },
          {
            label: "Lost",
            help: "Mark not converted.",
            icon: XCircle,
            run: (id: number) => api.status(id, "lost")
          }
        ]
      : []),
    ...(status !== "archived" && status !== "won"
      ? [
          {
            label: "Archive",
            help: "Remove from cockpit.",
            icon: Archive,
            run: (id: number) => api.status(id, "archived")
          }
        ]
      : []),
    ...(!blocked && status !== "won" && status !== "lost" && status !== "archived"
      ? [
          {
            label: "Do not contact",
            help: "Block outreach suggestions.",
            icon: Ban,
            variant: "danger" as const,
            run: api.doNotContact
          }
        ]
      : [])
  ];
}

export function nextStepCopy(status: string, blocked: boolean) {
  if (blocked) return "Outreach blocked.";
  if (status === "discovered") return "Enrich first.";
  if (status === "enriched" || status === "qualified")
    return "Generate or import a website before outreach.";
  if (status === "draft_ready" || status === "externally_imported")
    return "Draft the first email when ready.";
  if (status === "email_drafted") return "Send manually, then mark sent.";
  if (status === "contacted") return "Paste replies or set follow-up.";
  if (status === "replied" || status === "follow_up_needed" || status === "proposal_sent") {
    return "Continue or close the thread.";
  }
  if (status === "won" || status === "lost" || status === "archived") return "Closed.";
  return "Choose the next available step for this lead.";
}

export function isJobResult(data: unknown): data is JobResult {
  return Boolean(
    data &&
      typeof data === "object" &&
      "status" in data &&
      "type" in data &&
      "result_json" in data
  );
}
