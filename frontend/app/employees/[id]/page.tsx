"use client";

import React, { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import {
  ChevronLeft,
  DollarSign,
  Calendar,
  Building,
  Mail,
  Globe,
  User,
  Shield,
  Clock,
  PlusCircle,
  AlertCircle,
  RefreshCw,
} from "lucide-react";
import { Sidebar } from "@/components/layout/Sidebar";
import { Navbar } from "@/components/layout/Navbar";
import { SalaryChangeDialog } from "@/components/salary/SalaryChangeDialog";
import { SalaryHistoryTimeline } from "@/components/salary/SalaryHistoryTimeline";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { api, EmployeeDetail, SalaryRecord } from "@/lib/api";
import { formatCurrency, formatDate } from "@/lib/utils";

export default function EmployeeProfilePage() {
  const params = useParams();
  const router = useRouter();
  const employeeId = params?.id as string;

  const [employee, setEmployee] = useState<EmployeeDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);

  const loadEmployee = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getEmployee(employeeId);
      setEmployee(data);
    } catch (err: any) {
      setError(err.message || "Failed to load employee details.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (employeeId) {
      loadEmployee();
    }
  }, [employeeId]);

  const handleSalarySuccess = (newRecord: SalaryRecord) => {
    // Reload employee profile with updated salary timeline
    loadEmployee();
  };

  const getStatusBadge = (status: string) => {
    switch (status?.toUpperCase()) {
      case "ACTIVE":
        return <Badge variant="success">Active</Badge>;
      case "TERMINATED":
        return <Badge variant="destructive">Terminated</Badge>;
      case "ON_LEAVE":
        return <Badge variant="warning">On Leave</Badge>;
      default:
        return <Badge variant="secondary">{status}</Badge>;
    }
  };

  return (
    <div className="flex min-h-screen bg-slate-50 dark:bg-slate-950">
      <Sidebar />

      <div className="flex-1 pl-64">
        <Navbar
          title="Employee Compensation Profile"
          description={employee ? `${employee.full_name} (${employee.employee_number})` : "Loading..."}
        />

        <main className="p-8 space-y-6 max-w-6xl mx-auto">
          {/* Back Navigation Bar */}
          <div className="flex items-center justify-between">
            <Link
              href="/employees"
              className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-indigo-600 transition-colors"
            >
              <ChevronLeft className="h-4 w-4" />
              <span>Back to Employee Directory</span>
            </Link>

            {employee && (
              <Button
                onClick={() => setDialogOpen(true)}
                className="gap-1.5 bg-indigo-600 hover:bg-indigo-700 text-white shadow-md shadow-indigo-600/20"
              >
                <PlusCircle className="h-4 w-4" />
                <span>Record Salary Change</span>
              </Button>
            )}
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
                onClick={loadEmployee}
                className="gap-1 border-rose-300 bg-white hover:bg-rose-100"
              >
                <RefreshCw className="h-3.5 w-3.5" />
                Retry
              </Button>
            </div>
          )}

          {loading ? (
            <div className="space-y-6">
              <Skeleton className="h-44 w-full rounded-xl" />
              <Skeleton className="h-80 w-full rounded-xl" />
            </div>
          ) : employee ? (
            <div className="space-y-6">
              {/* Profile Card & Compensation Highlight */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Employee Details Card */}
                <Card className="lg:col-span-2">
                  <CardHeader className="pb-3 border-b border-slate-100 dark:border-slate-800">
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <div className="flex items-center gap-3">
                        <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-indigo-100 text-indigo-700 font-bold text-lg dark:bg-indigo-950 dark:text-indigo-300">
                          {employee.first_name[0]}{employee.last_name[0]}
                        </div>
                        <div>
                          <CardTitle className="text-xl font-bold text-slate-900 dark:text-white">
                            {employee.full_name}
                          </CardTitle>
                          <p className="text-xs font-mono font-medium text-indigo-600 dark:text-indigo-400">
                            {employee.employee_number}
                          </p>
                        </div>
                      </div>
                      {getStatusBadge(employee.employment_status)}
                    </div>
                  </CardHeader>

                  <CardContent className="pt-4 grid grid-cols-2 sm:grid-cols-3 gap-4 text-xs">
                    <div>
                      <span className="text-slate-400 flex items-center gap-1 mb-1">
                        <Mail className="h-3.5 w-3.5 text-slate-400" />
                        Work Email
                      </span>
                      <span className="font-medium text-slate-800 dark:text-slate-200 break-all">
                        {employee.email}
                      </span>
                    </div>

                    <div>
                      <span className="text-slate-400 flex items-center gap-1 mb-1">
                        <Building className="h-3.5 w-3.5 text-slate-400" />
                        Department
                      </span>
                      <span className="font-semibold text-slate-800 dark:text-slate-200">
                        {employee.department.name}
                      </span>
                    </div>

                    <div>
                      <span className="text-slate-400 flex items-center gap-1 mb-1">
                        <Globe className="h-3.5 w-3.5 text-slate-400" />
                        Country
                      </span>
                      <span className="font-semibold text-slate-800 dark:text-slate-200">
                        {employee.country_code}
                      </span>
                    </div>

                    <div>
                      <span className="text-slate-400 flex items-center gap-1 mb-1">
                        <Calendar className="h-3.5 w-3.5 text-slate-400" />
                        Employment Start Date
                      </span>
                      <span className="font-medium text-slate-800 dark:text-slate-200">
                        {formatDate(employee.employment_start_date)}
                      </span>
                    </div>

                    <div>
                      <span className="text-slate-400 flex items-center gap-1 mb-1">
                        <Clock className="h-3.5 w-3.5 text-slate-400" />
                        Created In System
                      </span>
                      <span className="font-medium text-slate-800 dark:text-slate-200">
                        {formatDate(employee.created_at)}
                      </span>
                    </div>

                    <div>
                      <span className="text-slate-400 flex items-center gap-1 mb-1">
                        <Shield className="h-3.5 w-3.5 text-slate-400" />
                        Salary Records Count
                      </span>
                      <span className="font-semibold text-indigo-600 dark:text-indigo-400">
                        {employee.salary_history.length} records
                      </span>
                    </div>
                  </CardContent>
                </Card>

                {/* Current Active Compensation Highlight */}
                <Card className="border-indigo-200 bg-gradient-to-br from-indigo-50/70 to-white dark:border-indigo-900 dark:from-indigo-950/40 dark:to-slate-900 flex flex-col justify-between">
                  <CardHeader className="pb-2">
                    <span className="text-xs font-semibold uppercase tracking-wider text-indigo-600 dark:text-indigo-400">
                      Active Effective Salary
                    </span>
                    <CardTitle className="text-3xl font-extrabold text-slate-900 dark:text-white mt-1">
                      {formatCurrency(employee.current_salary, employee.currency || "USD")}
                    </CardTitle>
                    <p className="text-xs text-slate-500 font-medium">
                      Currency: <strong className="text-slate-800 dark:text-slate-200">{employee.currency}</strong> (ISO 4217)
                    </p>
                  </CardHeader>

                  <CardContent className="pt-2">
                    <Button
                      onClick={() => setDialogOpen(true)}
                      className="w-full bg-indigo-600 hover:bg-indigo-700 text-white shadow-sm"
                    >
                      Propose Salary Change
                    </Button>
                  </CardContent>
                </Card>
              </div>

              {/* Salary History Timeline */}
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="text-lg font-semibold">Compensation History & Audit</CardTitle>
                      <CardDescription>
                        Full chronological record of effective-dated compensation periods
                      </CardDescription>
                    </div>
                    <Badge variant="outline" className="text-xs">
                      {employee.salary_history.length} Total Changes
                    </Badge>
                  </div>
                </CardHeader>

                <CardContent className="pt-2">
                  <SalaryHistoryTimeline history={employee.salary_history} />
                </CardContent>
              </Card>

              {/* Salary Change Dialog Modal */}
              <SalaryChangeDialog
                open={dialogOpen}
                onOpenChange={setDialogOpen}
                employee={employee}
                onSuccess={handleSalarySuccess}
              />
            </div>
          ) : null}
        </main>
      </div>
    </div>
  );
}
