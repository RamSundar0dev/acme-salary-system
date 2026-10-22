"use client";

import React, { useEffect, useState } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { Navbar } from "@/components/layout/Navbar";
import { EmployeeTable } from "@/components/employees/EmployeeTable";
import { api, Department, PaginatedEmployees } from "@/lib/api";
import { AlertCircle, RefreshCw, Download } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function EmployeesPage() {
  const [data, setData] = useState<PaginatedEmployees | null>(null);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Table state
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(15);
  const [search, setSearch] = useState("");
  const [country, setCountry] = useState("");
  const [departmentId, setDepartmentId] = useState("");
  const [status, setStatus] = useState("");
  const [sortBy, setSortBy] = useState("employee_number");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc");

  const loadEmployees = async () => {
    setLoading(true);
    setError(null);
    try {
      const [empData, deptsData] = await Promise.all([
        api.getEmployees({
          page,
          page_size: pageSize,
          search: search || undefined,
          country_code: country || undefined,
          department_id: departmentId || undefined,
          employment_status: status || undefined,
          sort_by: sortBy,
          sort_order: sortOrder,
        }),
        departments.length === 0 ? api.getDepartments() : Promise.resolve(departments),
      ]);

      setData(empData);
      if (departments.length === 0) setDepartments(deptsData);
    } catch (err: any) {
      setError(err.message || "Failed to load employees from backend API.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadEmployees();
  }, [page, pageSize, search, country, departmentId, status, sortBy, sortOrder]);

  const handleSortChange = (col: string) => {
    if (sortBy === col) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortBy(col);
      setSortOrder("asc");
    }
  };

  const handleFilterChange = (filters: { country?: string; departmentId?: string; status?: string }) => {
    setPage(1); // Reset to page 1 on filter change
    if (filters.country !== undefined) setCountry(filters.country);
    if (filters.departmentId !== undefined) setDepartmentId(filters.departmentId);
    if (filters.status !== undefined) setStatus(filters.status);
  };

  const exportUrl = api.getExportUrl({
    country_code: country || undefined,
    department_id: departmentId || undefined,
    employment_status: status || undefined,
    search: search || undefined,
  });

  return (
    <div className="flex min-h-screen bg-slate-50 dark:bg-slate-950">
      <Sidebar />

      <div className="flex-1 pl-64">
        <Navbar
          title="Employee Directory"
          description="Server-side indexed search, filtering, and compensation management across 10,000 records"
        />

        <main className="p-8 space-y-6 max-w-7xl mx-auto">
          {/* Header Action Bar */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h2 className="text-xl font-bold text-slate-900 dark:text-white">
                Workforce Records
              </h2>
              <p className="text-xs text-slate-500">
                Paginated server-side queries bounded to maximum 100 records per page.
              </p>
            </div>

            <div className="flex items-center gap-3">
              <a href={exportUrl} target="_blank" rel="noreferrer">
                <Button variant="outline" size="sm" className="gap-1.5 text-xs">
                  <Download className="h-3.5 w-3.5 text-emerald-600" />
                  <span>Export Filtered CSV</span>
                </Button>
              </a>
            </div>
          </div>

          {error && (
            <div className="flex items-center justify-between rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-800 dark:border-rose-900 dark:bg-rose-950 dark:text-rose-300">
              <div className="flex items-center gap-2">
                <AlertCircle className="h-5 w-5 text-rose-600 shrink-0" />
                <span>{error}</span>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={loadEmployees}
                className="gap-1 border-rose-300 bg-white hover:bg-rose-100"
              >
                <RefreshCw className="h-3.5 w-3.5" />
                Retry
              </Button>
            </div>
          )}

          <EmployeeTable
            data={data}
            departments={departments}
            loading={loading}
            page={page}
            pageSize={pageSize}
            search={search}
            country={country}
            departmentId={departmentId}
            status={status}
            sortBy={sortBy}
            sortOrder={sortOrder}
            onPageChange={setPage}
            onPageSizeChange={(sz) => { setPageSize(sz); setPage(1); }}
            onSearchChange={(s) => { setSearch(s); setPage(1); }}
            onFilterChange={handleFilterChange}
            onSortChange={handleSortChange}
          />
        </main>
      </div>
    </div>
  );
}
