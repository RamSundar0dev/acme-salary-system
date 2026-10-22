"use client";

import React, { useState } from "react";
import { AlertCircle, CheckCircle2, DollarSign, Calendar, FileText, ArrowRight } from "lucide-react";
import {
  Dialog,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { api, EmployeeDetail, SalaryRecord } from "@/lib/api";
import { formatCurrency, formatDate } from "@/lib/utils";

interface SalaryChangeDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  employee: EmployeeDetail;
  onSuccess: (newRecord: SalaryRecord) => void;
}

const SUPPORTED_CURRENCIES = ["USD", "EUR", "GBP", "CAD", "INR", "AUD", "SGD", "JPY"];

const REASONS = [
  { value: "MERIT_INCREASE", label: "Merit Increase / Performance Review" },
  { value: "PROMOTION", label: "Promotion / Level Advancement" },
  { value: "MARKET_ADJUSTMENT", label: "Market Compensation Adjustment" },
  { value: "ROLE_CHANGE", label: "Internal Role or Department Transfer" },
  { value: "CORRECTION", label: "Data Entry Correction (Error Fix)" },
];

export function SalaryChangeDialog({
  open,
  onOpenChange,
  employee,
  onSuccess,
}: SalaryChangeDialogProps) {
  const [step, setStep] = useState<"form" | "confirm">("form");
  const [amount, setAmount] = useState<string>("");
  const [currency, setCurrency] = useState<string>(employee.currency || "USD");
  const [effectiveFrom, setEffectiveFrom] = useState<string>(
    new Date().toISOString().split("T")[0]
  );
  const [changeReason, setChangeReason] = useState<string>("MERIT_INCREASE");
  const [isCorrection, setIsCorrection] = useState<boolean>(false);
  const [correctionNotes, setCorrectionNotes] = useState<string>("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const resetForm = () => {
    setStep("form");
    setAmount("");
    setCurrency(employee.currency || "USD");
    setEffectiveFrom(new Date().toISOString().split("T")[0]);
    setChangeReason("MERIT_INCREASE");
    setIsCorrection(false);
    setCorrectionNotes("");
    setError(null);
  };

  const handleReasonChange = (val: string) => {
    setChangeReason(val);
    if (val === "CORRECTION") {
      setIsCorrection(true);
    } else {
      setIsCorrection(false);
    }
  };

  const handleProceedToConfirm = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    const numAmount = parseFloat(amount);
    if (isNaN(numAmount) || numAmount <= 0) {
      setError("Salary amount must be a positive number.");
      return;
    }

    if (!effectiveFrom) {
      setError("Effective date is required.");
      return;
    }

    if (isCorrection && !correctionNotes.trim()) {
      setError("Correction notes are required for audit compliance when recording a data correction.");
      return;
    }

    setStep("confirm");
  };

  const handleSubmit = async () => {
    setLoading(true);
    setError(null);

    try {
      const record = await api.recordSalaryChange(employee.id, {
        amount: parseFloat(amount),
        currency: currency,
        effective_from: effectiveFrom,
        effective_to: null,
        change_reason: changeReason,
        is_correction: isCorrection,
        correction_notes: isCorrection ? correctionNotes : null,
      });

      onSuccess(record);
      onOpenChange(false);
      resetForm();
    } catch (err: any) {
      setError(err.message || "Failed to record salary change. Please verify parameters.");
      setStep("form");
    } finally {
      setLoading(false);
    }
  };

  const currentSal = employee.current_salary || 0;
  const newSal = parseFloat(amount) || 0;
  const delta = newSal - currentSal;
  const percentDelta = currentSal > 0 ? ((delta / currentSal) * 100).toFixed(1) : "N/A";

  return (
    <Dialog open={open} onOpenChange={(o) => { onOpenChange(o); if (!o) resetForm(); }}>
      <DialogHeader>
        <DialogTitle className="flex items-center gap-2 text-slate-900 dark:text-white">
          <DollarSign className="h-5 w-5 text-indigo-600" />
          {step === "form" ? "Record Compensation Change" : "Confirm Compensation Change"}
        </DialogTitle>
        <DialogDescription>
          {step === "form"
            ? `Update compensation for ${employee.full_name} (${employee.employee_number})`
            : "Review proposed salary adjustment and audit attribution before committing"}
        </DialogDescription>
      </DialogHeader>

      {error && (
        <div className="mb-4 flex items-start gap-2.5 rounded-lg border border-rose-200 bg-rose-50 p-3 text-xs text-rose-800 dark:border-rose-900 dark:bg-rose-950 dark:text-rose-300">
          <AlertCircle className="h-4 w-4 shrink-0 text-rose-600 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      {step === "form" ? (
        <form onSubmit={handleProceedToConfirm} className="space-y-4">
          {/* Current Salary Benchmark Banner */}
          <div className="rounded-lg border border-slate-100 bg-slate-50 p-3 dark:border-slate-800 dark:bg-slate-800/50 flex items-center justify-between text-xs">
            <span className="text-slate-500">Current Effective Salary:</span>
            <span className="font-bold text-slate-900 dark:text-white">
              {formatCurrency(employee.current_salary, employee.currency || "USD")} ({employee.currency})
            </span>
          </div>

          {/* Amount & Currency */}
          <div className="grid grid-cols-3 gap-3">
            <div className="col-span-2 space-y-1">
              <label className="text-xs font-semibold text-slate-700 dark:text-slate-300">
                New Salary Amount *
              </label>
              <div className="relative">
                <Input
                  type="number"
                  step="0.01"
                  min="1"
                  required
                  placeholder="e.g. 115000"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  className="font-semibold text-base"
                />
              </div>
            </div>

            <div className="col-span-1 space-y-1">
              <label className="text-xs font-semibold text-slate-700 dark:text-slate-300">
                Currency *
              </label>
              <select
                value={currency}
                onChange={(e) => setCurrency(e.target.value)}
                className="h-9 w-full rounded-md border border-slate-200 bg-background px-3 text-sm font-medium focus:border-indigo-500 focus:outline-none dark:border-slate-700"
              >
                {SUPPORTED_CURRENCIES.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Effective From Date */}
          <div className="space-y-1">
            <label className="text-xs font-semibold text-slate-700 dark:text-slate-300">
              Effective From Date (Inclusive) *
            </label>
            <Input
              type="date"
              required
              value={effectiveFrom}
              onChange={(e) => setEffectiveFrom(e.target.value)}
            />
            <p className="text-[11px] text-slate-400">
              The existing active salary period will automatically end on this date.
            </p>
          </div>

          {/* Reason Selector */}
          <div className="space-y-1">
            <label className="text-xs font-semibold text-slate-700 dark:text-slate-300">
              Change Reason *
            </label>
            <select
              value={changeReason}
              onChange={(e) => handleReasonChange(e.target.value)}
              className="h-9 w-full rounded-md border border-slate-200 bg-background px-3 text-sm focus:border-indigo-500 focus:outline-none dark:border-slate-700"
            >
              {REASONS.map((r) => (
                <option key={r.value} value={r.value}>
                  {r.label}
                </option>
              ))}
            </select>
          </div>

          {/* Correction Checkbox & Notes */}
          <div className="pt-2">
            <label className="flex items-center gap-2 text-xs font-medium text-slate-700 dark:text-slate-300 cursor-pointer">
              <input
                type="checkbox"
                checked={isCorrection}
                onChange={(e) => setIsCorrection(e.target.checked)}
                className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
              />
              <span>Mark as historical data correction (updates active record in-place)</span>
            </label>

            {isCorrection && (
              <div className="mt-2 space-y-1 animate-in fade-in-50">
                <label className="text-xs font-semibold text-amber-700 dark:text-amber-400">
                  Audit Explanation Notes *
                </label>
                <textarea
                  rows={2}
                  required
                  placeholder="Explain the data entry discrepancy being corrected..."
                  value={correctionNotes}
                  onChange={(e) => setCorrectionNotes(e.target.value)}
                  className="w-full rounded-md border border-amber-300 bg-amber-50/40 p-2 text-xs text-slate-800 placeholder:text-slate-400 focus:border-indigo-500 focus:outline-none dark:border-amber-700 dark:bg-amber-950/30 dark:text-slate-200"
                />
              </div>
            )}
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
            >
              Cancel
            </Button>
            <Button type="submit" className="gap-1.5 bg-indigo-600 hover:bg-indigo-700">
              <span>Review Proposed Change</span>
              <ArrowRight className="h-4 w-4" />
            </Button>
          </DialogFooter>
        </form>
      ) : (
        /* Review / Confirmation Step */
        <div className="space-y-4">
          <div className="rounded-xl border border-indigo-100 bg-indigo-50/50 p-4 dark:border-indigo-900 dark:bg-indigo-950/40 space-y-3">
            <div className="flex items-center justify-between text-xs border-b border-indigo-100 pb-2 dark:border-indigo-800/60">
              <span className="text-slate-500">Employee:</span>
              <span className="font-semibold text-slate-900 dark:text-white">
                {employee.full_name} ({employee.employee_number})
              </span>
            </div>

            <div className="flex items-center justify-between text-xs border-b border-indigo-100 pb-2 dark:border-indigo-800/60">
              <span className="text-slate-500">Current Salary:</span>
              <span className="font-medium text-slate-700 dark:text-slate-300">
                {formatCurrency(currentSal, employee.currency || "USD")}
              </span>
            </div>

            <div className="flex items-center justify-between text-xs border-b border-indigo-100 pb-2 dark:border-indigo-800/60">
              <span className="text-slate-500">Proposed New Salary:</span>
              <span className="font-bold text-lg text-indigo-700 dark:text-indigo-400">
                {formatCurrency(newSal, currency)}
              </span>
            </div>

            <div className="flex items-center justify-between text-xs border-b border-indigo-100 pb-2 dark:border-indigo-800/60">
              <span className="text-slate-500">Adjustment Delta:</span>
              <span className={`font-semibold ${delta >= 0 ? "text-emerald-600" : "text-rose-600"}`}>
                {delta >= 0 ? "+" : ""}{formatCurrency(delta, currency)} ({percentDelta}%)
              </span>
            </div>

            <div className="flex items-center justify-between text-xs border-b border-indigo-100 pb-2 dark:border-indigo-800/60">
              <span className="text-slate-500">Effective Date:</span>
              <span className="font-medium text-slate-900 dark:text-white">
                {formatDate(effectiveFrom)}
              </span>
            </div>

            <div className="flex items-center justify-between text-xs">
              <span className="text-slate-500">Classification:</span>
              <Badge variant={isCorrection ? "warning" : "secondary"}>
                {changeReason.replace("_", " ")}
              </Badge>
            </div>
          </div>

          <p className="text-xs text-slate-500 italic">
            This action will be permanently recorded in the immutable audit log under your HR Manager identity.
          </p>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              disabled={loading}
              onClick={() => setStep("form")}
            >
              Back to Edit
            </Button>
            <Button
              type="button"
              disabled={loading}
              onClick={handleSubmit}
              className="bg-emerald-600 hover:bg-emerald-700 text-white gap-1.5"
            >
              <CheckCircle2 className="h-4 w-4" />
              {loading ? "Recording..." : "Confirm & Save Salary"}
            </Button>
          </DialogFooter>
        </div>
      )}
    </Dialog>
  );
}
