"use client";

import React, { useEffect, useState } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { Navbar } from "@/components/layout/Navbar";
import { MetricCards } from "@/components/dashboard/MetricCards";
import { CompensationChart } from "@/components/dashboard/CompensationChart";
import { RecentChangesTable } from "@/components/dashboard/RecentChangesTable";
import { api, DashboardSummary, Department, DistributionResponse } from "@/lib/api";
import { AlertCircle, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function DashboardPage() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [distribution, setDistribution] = useState<DistributionResponse | null>(null);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [country, setCountry] = useState<string>("");
  const [departmentId, setDepartmentId] = useState<string>("");
  const [currency, setCurrency] = useState<string>("USD");

  const loadDashboardData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [sumData, distData, deptsData] = await Promise.all([
        api.getDashboardSummary({
          country_code: country || undefined,
          department_id: departmentId || undefined,
          currency: currency || undefined,
        }),
        api.getDistribution(currency || undefined),
        departments.length === 0 ? api.getDepartments() : Promise.resolve(departments),
      ]);

      setSummary(sumData);
      setDistribution(distData);
      if (departments.length === 0) setDepartments(deptsData);
    } catch (err: any) {
      setError(err.message || "Failed to load dashboard metrics from backend APIs.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, [country, departmentId, currency]);

  const handleFilterChange = (filters: { country?: string; department?: string; currency?: string }) => {
    if (filters.country !== undefined) setCountry(filters.country);
    if (filters.department !== undefined) setDepartmentId(filters.department);
    if (filters.currency !== undefined) setCurrency(filters.currency || "USD");
  };

  return (
    <div className="flex min-h-screen bg-slate-50 dark:bg-slate-950">
      <Sidebar />

      <div className="flex-1 pl-64">
        <Navbar
          title="HR Executive Dashboard"
          description="Compensation metrics and workforce analytics across 10,000 employees"
        />

        <main className="p-8 space-y-8 max-w-7xl mx-auto">
          {error && (
            <div className="flex items-center justify-between rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-800 dark:border-rose-900 dark:bg-rose-950 dark:text-rose-300">
              <div className="flex items-center gap-2">
                <AlertCircle className="h-5 w-5 text-rose-600 shrink-0" />
                <span>{error}</span>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={loadDashboardData}
                className="gap-1 border-rose-300 bg-white hover:bg-rose-100"
              >
                <RefreshCw className="h-3.5 w-3.5" />
                Retry
              </Button>
            </div>
          )}

          {/* KPI Stat Cards and Currency Isolation Grid */}
          <MetricCards
            summary={summary}
            departments={departments}
            selectedCountry={country}
            selectedDepartment={departmentId}
            selectedCurrency={currency}
            onFilterChange={handleFilterChange}
          />

          {/* Recharts Visualizations & Recent Audit Feed */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <CompensationChart
              distribution={distribution}
              metricsByDepartment={summary?.metrics_by_department || []}
              metricsByCountry={summary?.metrics_by_country || []}
              activeCurrency={currency}
            />

            <RecentChangesTable changes={summary?.recent_changes || []} />
          </div>
        </main>
      </div>
    </div>
  );
}
