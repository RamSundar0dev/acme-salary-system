"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  Search,
  ChevronLeft,
  ChevronRight,
  ArrowUpDown,
  Filter,
  Eye,
  FileSpreadsheet,
} from "lucide-react";
import {
  Department,
  PaginatedEmployees,
  EmployeeSummary,
} from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { formatCurrency, formatDate } from "@/lib/utils";

interface EmployeeTableProps {
  data: PaginatedEmployees | null;
  departments: Department[];
  loading: boolean;
  page: number;
  pageSize: number;
  search: string;
  country: string;
  departmentId: string;
  status: string;
  sortBy: string;
  sortOrder: string;
  onPageChange: (newPage: number) => void;
  onPageSizeChange: (newSize: number) => void;
  onSearchChange: (search: string) => void;
  onFilterChange: (filters: { country?: string; departmentId?: string; status?: string }) => void;
  onSortChange: (column: string) => void;
}

export function EmployeeTable({
  data,
  departments,
  loading,
  page,
  pageSize,
  search,
  country,
  departmentId,
  status,
  sortBy,
  sortOrder,
  onPageChange,
  onPageSizeChange,
  onSearchChange,
  onFilterChange,
  onSortChange,
}: EmployeeTableProps) {
  const [searchInput, setSearchInput] = useState(search);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearchChange(searchInput);
  };

  const getStatusBadge = (empStatus: string) => {
    switch (empStatus.toUpperCase()) {
      case "ACTIVE":
        return <Badge variant="success">Active</Badge>;
      case "TERMINATED":
        return <Badge variant="destructive">Terminated</Badge>;
      case "ON_LEAVE":
        return <Badge variant="warning">On Leave</Badge>;
      default:
        return <Badge variant="secondary">{empStatus}</Badge>;
    }
  };

  const total = data?.total || 0;
  const startItem = total === 0 ? 0 : (page - 1) * pageSize + 1;
  const endItem = Math.min(page * pageSize, total);
  const totalPages = data?.total_pages || 1;

  return (
    <div className="space-y-4">
      {/* Search & Filter Header */}
      <div className="flex flex-col gap-3 rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900 md:flex-row md:items-center md:justify-between">
        {/* Search Bar */}
        <form onSubmit={handleSearchSubmit} className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
          <Input
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            placeholder="Search by ID, name, or work email..."
            className="pl-9 bg-slate-50 border-slate-200 dark:bg-slate-800 dark:border-slate-700"
          />
        </form>

        {/* Filter Controls */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Country */}
          <select
            value={country}
            onChange={(e) => onFilterChange({ country: e.target.value })}
            className="h-9 rounded-md border border-slate-200 bg-slate-50 px-3 text-xs font-medium text-slate-700 shadow-sm focus:border-indigo-500 focus:outline-none dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200"
          >
            <option value="">All Countries</option>
            <option value="US">United States (US)</option>
            <option value="GB">United Kingdom (GB)</option>
            <option value="DE">Germany (DE)</option>
            <option value="CA">Canada (CA)</option>
            <option value="IN">India (IN)</option>
            <option value="AU">Australia (AU)</option>
            <option value="SG">Singapore (SG)</option>
            <option value="JP">Japan (JP)</option>
          </select>

          {/* Department */}
          <select
            value={departmentId}
            onChange={(e) => onFilterChange({ departmentId: e.target.value })}
            className="h-9 rounded-md border border-slate-200 bg-slate-50 px-3 text-xs font-medium text-slate-700 shadow-sm focus:border-indigo-500 focus:outline-none dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200"
          >
            <option value="">All Departments</option>
            {departments.map((d) => (
              <option key={d.id} value={d.id.toString()}>
                {d.name}
              </option>
            ))}
          </select>

          {/* Status */}
          <select
            value={status}
            onChange={(e) => onFilterChange({ status: e.target.value })}
            className="h-9 rounded-md border border-slate-200 bg-slate-50 px-3 text-xs font-medium text-slate-700 shadow-sm focus:border-indigo-500 focus:outline-none dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200"
          >
            <option value="">All Statuses</option>
            <option value="ACTIVE">Active</option>
            <option value="TERMINATED">Terminated</option>
            <option value="ON_LEAVE">On Leave</option>
          </select>
        </div>
      </div>

      {/* Table Container */}
      <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="border-b border-slate-200 bg-slate-50 text-xs font-semibold uppercase tracking-wider text-slate-500 dark:border-slate-800 dark:bg-slate-800/50">
              <tr>
                <th
                  onClick={() => onSortChange("employee_number")}
                  className="cursor-pointer px-6 py-3.5 hover:text-slate-900 dark:hover:text-white"
                >
                  <div className="flex items-center gap-1">
                    Employee ID
                    <ArrowUpDown className="h-3 w-3" />
                  </div>
                </th>
                <th
                  onClick={() => onSortChange("last_name")}
                  className="cursor-pointer px-6 py-3.5 hover:text-slate-900 dark:hover:text-white"
                >
                  <div className="flex items-center gap-1">
                    Name & Email
                    <ArrowUpDown className="h-3 w-3" />
                  </div>
                </th>
                <th
                  onClick={() => onSortChange("country_code")}
                  className="cursor-pointer px-6 py-3.5 hover:text-slate-900 dark:hover:text-white"
                >
                  <div className="flex items-center gap-1">
                    Country
                    <ArrowUpDown className="h-3 w-3" />
                  </div>
                </th>
                <th className="px-6 py-3.5">Department</th>
                <th
                  onClick={() => onSortChange("employment_status")}
                  className="cursor-pointer px-6 py-3.5 hover:text-slate-900 dark:hover:text-white"
                >
                  <div className="flex items-center gap-1">
                    Status
                    <ArrowUpDown className="h-3 w-3" />
                  </div>
                </th>
                <th className="px-6 py-3.5 text-right">Current Salary</th>
                <th className="px-6 py-3.5 text-center">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
              {loading ? (
                Array.from({ length: 8 }).map((_, idx) => (
                  <tr key={idx}>
                    <td className="px-6 py-4"><Skeleton className="h-4 w-20" /></td>
                    <td className="px-6 py-4"><Skeleton className="h-4 w-36 mb-1" /><Skeleton className="h-3 w-28" /></td>
                    <td className="px-6 py-4"><Skeleton className="h-4 w-12" /></td>
                    <td className="px-6 py-4"><Skeleton className="h-4 w-24" /></td>
                    <td className="px-6 py-4"><Skeleton className="h-5 w-16" /></td>
                    <td className="px-6 py-4 text-right"><Skeleton className="h-4 w-24 ml-auto" /></td>
                    <td className="px-6 py-4 text-center"><Skeleton className="h-8 w-16 mx-auto" /></td>
                  </tr>
                ))
              ) : data && data.items.length > 0 ? (
                data.items.map((emp) => (
                  <tr
                    key={emp.id}
                    className="hover:bg-slate-50/70 transition-colors dark:hover:bg-slate-800/50"
                  >
                    <td className="px-6 py-4 font-mono font-medium text-xs text-indigo-600 dark:text-indigo-400">
                      {emp.employee_number}
                    </td>
                    <td className="px-6 py-4">
                      <div className="font-medium text-slate-900 dark:text-white">
                        {emp.full_name}
                      </div>
                      <div className="text-xs text-slate-400">{emp.email}</div>
                    </td>
                    <td className="px-6 py-4">
                      <span className="inline-flex items-center rounded bg-slate-100 px-2 py-0.5 text-xs font-semibold text-slate-700 dark:bg-slate-800 dark:text-slate-300">
                        {emp.country_code}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-slate-600 dark:text-slate-300">
                      {emp.department_name}
                    </td>
                    <td className="px-6 py-4">{getStatusBadge(emp.employment_status)}</td>
                    <td className="px-6 py-4 text-right font-semibold text-slate-900 dark:text-white">
                      {formatCurrency(emp.current_salary, emp.currency || "USD")}
                      <span className="text-[10px] text-slate-400 ml-1 font-normal">
                        {emp.currency}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <Link href={`/employees/${emp.id}`}>
                        <Button variant="outline" size="sm" className="h-8 text-xs gap-1">
                          <Eye className="h-3.5 w-3.5" />
                          Profile
                        </Button>
                      </Link>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={7} className="px-6 py-12 text-center text-slate-400">
                    No employees matching the current search and filter criteria.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Footer */}
        <div className="flex flex-col sm:flex-row items-center justify-between border-t border-slate-200 px-6 py-4 dark:border-slate-800 gap-4">
          <div className="text-xs text-slate-500">
            Showing <span className="font-semibold text-slate-700 dark:text-slate-300">{startItem}</span> to{" "}
            <span className="font-semibold text-slate-700 dark:text-slate-300">{endItem}</span> of{" "}
            <span className="font-semibold text-slate-700 dark:text-slate-300">{total.toLocaleString()}</span> employees
          </div>

          <div className="flex items-center gap-4">
            {/* Page Size Selector */}
            <div className="flex items-center gap-2 text-xs text-slate-500">
              <span>Per page:</span>
              <select
                value={pageSize}
                onChange={(e) => onPageSizeChange(Number(e.target.value))}
                className="h-8 rounded border border-slate-200 bg-slate-50 px-2 text-xs font-medium focus:outline-none dark:border-slate-700 dark:bg-slate-800"
              >
                <option value={15}>15</option>
                <option value={25}>25</option>
                <option value={50}>50</option>
                <option value={100}>100</option>
              </select>
            </div>

            {/* Pagination Controls */}
            <div className="flex items-center gap-1">
              <Button
                variant="outline"
                size="sm"
                onClick={() => onPageChange(page - 1)}
                disabled={page <= 1 || loading}
                className="h-8 px-2"
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <span className="px-2 text-xs font-medium text-slate-600 dark:text-slate-400">
                Page {page} of {totalPages}
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => onPageChange(page + 1)}
                disabled={page >= totalPages || loading}
                className="h-8 px-2"
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
