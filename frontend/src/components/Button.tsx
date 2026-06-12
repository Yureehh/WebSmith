import { clsx } from "clsx";
import type { ButtonHTMLAttributes, PropsWithChildren } from "react";

type ButtonProps = PropsWithChildren<ButtonHTMLAttributes<HTMLButtonElement>> & {
  variant?: "primary" | "secondary" | "danger" | "quiet";
};

export function Button({ children, className, variant = "secondary", ...props }: ButtonProps) {
  return (
    <button
      className={clsx(
        "inline-flex min-h-10 items-center justify-center gap-2 rounded-md px-3 py-2 text-sm font-semibold transition duration-200 disabled:cursor-not-allowed disabled:opacity-45",
        variant === "primary" &&
          "bg-[linear-gradient(135deg,#0f172a,#0f766e_58%,#0891b2)] text-white shadow-[0_14px_32px_rgb(8_145_178/0.22)] hover:-translate-y-0.5 hover:shadow-[0_20px_42px_rgb(8_145_178/0.28)]",
        variant === "secondary" &&
          "border border-ink/12 bg-white text-ink shadow-[0_8px_22px_rgb(15_23_42/0.06)] hover:-translate-y-0.5 hover:border-cyan-500/45 hover:bg-cloud/70",
        variant === "danger" &&
          "bg-[linear-gradient(135deg,#f9735b,#d94635)] text-white shadow-[0_12px_28px_rgb(224_82_63/0.22)] hover:-translate-y-0.5",
        variant === "quiet" && "text-ink hover:bg-ink/5",
        className
      )}
      {...props}
    >
      {children}
    </button>
  );
}
