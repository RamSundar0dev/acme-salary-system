"use client";

import React from "react";
import { Users, UserCheck, UserX, Coins, Globe, Building } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { DashboardSummary, Department } from "@/lib/api";
import { formatCurrency } from "@/lib/utils";

interface MetricCardsProps {
  summary: DashboardSummary | null;
  departments: Department[];
  selectedCountry: string;
  selectedDepartment: string;
  selectedCurrency: string;
  onFilterChange: (filters: { country?: string; department?: string; currency?: string }) => void;
}

export function MetricCards({
  summary,
  departments,
  selectedCountry,
  selectedDepartment,
  selectedCurrency,
  onFilterChange,
}: MetricCardsProps) {
  const countries = [
    { code: "", label: "All Countries" },
    { code: "US", label: "United States (US)" },
    { code: "GB", label: "United Kingdom (GB)" },
    { code: "DE", label: "Germany (DE)" },
    { code: "CA", label: "Canada (CA)" },
    { code: "IN", label: "India (IN)" },
    { code: "AU", label: "Australia (AU)" },
    { code: "SG", label: "Singapore (SG)" },
    { code: "JP", label: "Japan (JP)" },
  ];

  const currencies = [
    { code: "", label: "All Currencies" },
    { code: "USD", label: "USD ($)" },
    { code: "EUR", label: "EUR (€)" },
    { code: "GBP", label: "GBP (£)" },
    { code: "CAD", label: "CAD ($)" },
    { code: "INR", label: "INR (₹)" },
    { code: "AUD", label: "AUD ($)" },
    { code: "SGD", label: "SGD ($)" },
    { code: "JPY", label: "JPY (¥)" },
  ];

  return (
    <div className="space-y-6">
      {/* Top Filter Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div className="flex items-center gap-2">
          <Globe className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
          <span className="text-sm font-semibold text-slate-800 dark:text-slate-200">
            Analytics Filters
          </span>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {/* Country Filter */}
          <select
            value={selectedCountry}
            onChange={(e) => onFilterChange({ country: e.target.value })}
            className="h-9 rounded-md border border-slate-200 bg-slate-50 px-3 text-xs font-medium text-slate-700 shadow-sm focus:border-indigo-500 focus:outline-none dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200"
          >
            {countries.map((c) => (
              <option key={c.code} value={c.code}>
                {c.label}
              </option>
            ))}
          </select>

          {/* Department Filter */}
          <select
            value={selectedDepartment}
            onChange={(e) => onFilterChange({ department: e.target.value })}
            className="h-9 rounded-md border border-slate-200 bg-slate-50 px-3 text-xs font-medium text-slate-700 shadow-sm focus:border-indigo-500 focus:outline-none dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200"
          >
            <option value="">All Departments</option>
            {departments.map((d) => (
              <option key={d.id} value={d.id.toString()}>
                {d.name}
              </option>
            ))}
          </select>

          {/* Currency Filter */}
          <select
            value={selectedCurrency}
            onChange={(e) => onFilterChange({ currency: e.target.value })}
            className="h-9 rounded-md border border-slate-200 bg-slate-50 px-3 text-xs font-medium text-slate-700 shadow-sm focus:border-indigo-500 focus:outline-none dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200"
          >
            {currencies.map((curr) => (
              <option key={curr.code} value={curr.code}>
                {curr.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Primary KPI Summary Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <Card className="hover:border-indigo-300 transition-colors">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-slate-500">Total Workforce</CardTitle>
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600 dark:bg-indigo-950/60 dark:text-indigo-400">
              <Users className="h-4 w-4" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
              {summary ? summary.total_employees.toLocaleString() : "..."}
            </div>
            <p className="text-xs text-slate-500 mt-1">Total recorded employees across ACME Corp</p>
          </CardContent>
        </Card>

        <Card className="hover:border-emerald-300 transition-colors">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-slate-500">Active Staff</CardTitle>
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-50 text-emerald-600 dark:bg-emerald-950/60 dark:text-emerald-400">
              <UserCheck className="h-4 w-4" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold tracking-tight text-emerald-600 dark:text-emerald-400">
              {summary ? summary.active_employees.toLocaleString() : "..."}
            </div>
            <p className="text-xs text-slate-500 mt-1">Currently receiving active compensation</p>
          </CardContent>
        </Card>

        <Card className="hover:border-slate-300 transition-colors">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-slate-500">Inactive / On Leave</CardTitle>
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400">
              <UserX className="h-4 w-4" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold tracking-tight text-slate-700 dark:text-slate-300">
              {summary ? summary.inactive_employees.toLocaleString() : "..."}
            </div>
            <p className="text-xs text-slate-500 mt-1">Terminated or temporarily on leave</p>
          </CardContent>
        </Card>
      </div>

      {/* Current Payroll Totals (Currency Isolated - Strict Compliance) */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Coins className="h-4 w-4 text-indigo-600" />
              <CardTitle className="text-base font-semibold">Active Payroll Totals by Currency</CardTitle>
            </div>
            <span className="text-xs text-slate-400 font-normal">
              Currencies strictly isolated without unverified FX blending
            </span>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4 lg:grid-cols-8">
            {summary?.payroll_by_currency.map((p) => (
              <div
                key={p.currency}
                className="flex flex-col rounded-lg border border-slate-100 bg-slate-50/70 p-3 dark:border-slate-800 dark:bg-slate-800/40"
              >
                <div className="flex items-center justify-between text-xs font-semibold text-slate-600 dark:text-slate-300 mb-1">
                  <span>{p.currency}</span>
                  <span className="rounded bg-indigo-100 px-1.5 py-0.2 text-[10px] text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300">
                    {p.headcount}
                  </span>
                </div>
                <div className="text-sm font-bold text-slate-900 dark:text-white truncate">
                  {formatCurrency(p.total_amount, p.currency)}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
