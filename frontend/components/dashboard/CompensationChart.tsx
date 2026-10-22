"use client";

import React, { useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { DistributionResponse, MetricByDimension } from "@/lib/api";
import { formatCurrency } from "@/lib/utils";

interface CompensationChartProps {
  distribution: DistributionResponse | null;
  metricsByDepartment: MetricByDimension[];
  metricsByCountry: MetricByDimension[];
  activeCurrency: string;
}

export function CompensationChart({
  distribution,
  metricsByDepartment,
  metricsByCountry,
  activeCurrency = "USD",
}: CompensationChartProps) {
  const [viewMode, setViewMode] = useState<"distribution" | "department" | "country">("distribution");

  // Filter distribution for active currency
  const currBuckets = distribution?.buckets_by_currency[activeCurrency] || [];
  const distData = currBuckets.map((b) => ({
    name: b.range_label,
    Employees: b.count,
  }));

  // Filter department metrics for active currency
  const deptData = metricsByDepartment
    .filter((m) => m.currency === activeCurrency)
    .map((m) => ({
      name: m.dimension,
      Average: Number(m.avg_salary),
      Median: Number(m.median_salary),
      Headcount: m.employee_count,
    }));

  return (
    <Card className="col-span-1 shadow-sm">
      <CardHeader className="flex flex-row items-center justify-between pb-4">
        <div>
          <CardTitle className="text-base font-semibold">Compensation Analytics</CardTitle>
          <CardDescription>
            {viewMode === "distribution"
              ? `Salary distribution buckets for ${activeCurrency}`
              : `Average vs. Median salary comparison (${activeCurrency})`}
          </CardDescription>
        </div>

        {/* Tab Toggle */}
        <div className="flex items-center rounded-lg border border-slate-200 bg-slate-50 p-1 text-xs dark:border-slate-800 dark:bg-slate-800">
          <button
            onClick={() => setViewMode("distribution")}
            className={`rounded-md px-3 py-1 font-medium transition-colors ${
              viewMode === "distribution"
                ? "bg-white text-indigo-700 shadow-sm dark:bg-slate-900 dark:text-indigo-400"
                : "text-slate-500 hover:text-slate-900 dark:text-slate-400"
            }`}
          >
            Distribution
          </button>
          <button
            onClick={() => setViewMode("department")}
            className={`rounded-md px-3 py-1 font-medium transition-colors ${
              viewMode === "department"
                ? "bg-white text-indigo-700 shadow-sm dark:bg-slate-900 dark:text-indigo-400"
                : "text-slate-500 hover:text-slate-900 dark:text-slate-400"
            }`}
          >
            By Department
          </button>
        </div>
      </CardHeader>

      <CardContent>
        <div className="h-[300px] w-full">
          {viewMode === "distribution" ? (
            distData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={distData} margin={{ top: 10, right: 10, left: 0, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                  <XAxis dataKey="name" stroke="#64748b" fontSize={12} tickLine={false} />
                  <YAxis stroke="#64748b" fontSize={12} tickLine={false} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#ffffff",
                      borderRadius: "8px",
                      border: "1px solid #e2e8f0",
                      boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)",
                    }}
                    formatter={(val: any) => [`${val} employees`, "Headcount"]}
                  />
                  <Bar dataKey="Employees" fill="#6366f1" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex h-full items-center justify-center text-sm text-slate-400">
                No distribution data available for {activeCurrency}
              </div>
            )
          ) : deptData.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={deptData} margin={{ top: 10, right: 10, left: 10, bottom: 30 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis
                  dataKey="name"
                  stroke="#64748b"
                  fontSize={11}
                  interval={0}
                  angle={-15}
                  textAnchor="end"
                  tickLine={false}
                />
                <YAxis
                  stroke="#64748b"
                  fontSize={11}
                  tickLine={false}
                  tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#ffffff",
                    borderRadius: "8px",
                    border: "1px solid #e2e8f0",
                  }}
                  formatter={(val: any, name: any) => [formatCurrency(val, activeCurrency), name]}
                />
                <Legend verticalAlign="top" height={36} />
                <Bar dataKey="Average" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                <Bar dataKey="Median" fill="#10b981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex h-full items-center justify-center text-sm text-slate-400">
              No department data available for {activeCurrency}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
