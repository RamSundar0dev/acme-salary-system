"use client";

import React from "react";
import { Check, Clock, Calendar, ArrowRight, Shield } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { SalaryRecord } from "@/lib/api";
import { formatCurrency, formatDate } from "@/lib/utils";

export function SalaryHistoryTimeline({ history }: { history: SalaryRecord[] }) {
  if (!history || history.length === 0) {
    return (
      <div className="flex h-36 items-center justify-center rounded-xl border border-dashed border-slate-200 p-6 text-sm text-slate-400">
        No compensation history records found.
      </div>
    );
  }

  // Sort descending by effective_from
  const sorted = [...history].sort(
    (a, b) => new Date(b.effective_from).getTime() - new Date(a.effective_from).getTime()
  );

  return (
    <div className="relative pl-6 space-y-6 before:absolute before:bottom-0 before:left-[11px] before:top-2 before:w-[2px] before:bg-slate-200 dark:before:bg-slate-800">
      {sorted.map((rec, index) => {
        const isCurrent = rec.effective_to === null;

        return (
          <div key={rec.id} className="relative group">
            {/* Timeline Node Marker */}
            <div
              className={`absolute -left-[30px] top-1.5 flex h-5 w-5 items-center justify-center rounded-full border-2 transition-transform group-hover:scale-110 ${
                isCurrent
                  ? "border-emerald-500 bg-emerald-500 text-white shadow-sm shadow-emerald-500/30"
                  : "border-slate-300 bg-white text-slate-400 dark:border-slate-700 dark:bg-slate-900"
              }`}
            >
              {isCurrent ? <Check className="h-3 w-3 stroke-[3]" /> : <Clock className="h-2.5 w-2.5" />}
            </div>

            {/* Content Card */}
            <div
              className={`rounded-xl border p-4 transition-all duration-200 ${
                isCurrent
                  ? "border-emerald-200 bg-emerald-50/30 shadow-sm dark:border-emerald-900/50 dark:bg-emerald-950/20"
                  : "border-slate-200 bg-white hover:border-slate-300 dark:border-slate-800 dark:bg-slate-900"
              }`}
            >
              <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
                <div className="flex items-center gap-2">
                  <span className="text-xl font-bold tracking-tight text-slate-900 dark:text-white">
                    {formatCurrency(rec.amount, rec.currency)}
                  </span>
                  <span className="text-xs font-semibold text-slate-500">{rec.currency}</span>
                </div>

                <div className="flex items-center gap-1.5">
                  {isCurrent && <Badge variant="success">Current Active</Badge>}
                  {rec.is_correction && <Badge variant="warning">Corrected Record</Badge>}
                  <Badge variant="secondary" className="text-xs">
                    {rec.change_reason.replace("_", " ")}
                  </Badge>
                </div>
              </div>

              {/* Effective Period Boundaries */}
              <div className="flex flex-wrap items-center gap-4 text-xs text-slate-500 dark:text-slate-400">
                <div className="flex items-center gap-1.5">
                  <Calendar className="h-3.5 w-3.5 text-slate-400" />
                  <span>
                    Effective: <strong className="text-slate-700 dark:text-slate-300">{formatDate(rec.effective_from)}</strong>
                    {" "}&rarr;{" "}
                    <strong className="text-slate-700 dark:text-slate-300">{rec.effective_to ? formatDate(rec.effective_to) : "Open-ended (Present)"}</strong>
                  </span>
                </div>

                <div className="text-[11px] text-slate-400">
                  Recorded: {formatDate(rec.created_at)}
                </div>
              </div>

              {rec.correction_notes && (
                <div className="mt-3 rounded-lg border border-amber-200 bg-amber-50/50 p-2.5 text-xs text-amber-800 dark:border-amber-900 dark:bg-amber-950/30 dark:text-amber-300">
                  <strong>Correction Reason:</strong> {rec.correction_notes}
                </div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
