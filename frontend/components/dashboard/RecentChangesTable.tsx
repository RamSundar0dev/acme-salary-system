"use client";

import React from "react";
import Link from "next/link";
import { ArrowUpRight, ArrowDownRight, History, ShieldAlert } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { RecentSalaryChange } from "@/lib/api";
import { formatCurrency, formatDate } from "@/lib/utils";

export function RecentChangesTable({ changes }: { changes: RecentSalaryChange[] }) {
  return (
    <Card className="col-span-1 shadow-sm">
      <CardHeader className="flex flex-row items-center justify-between pb-3">
        <div>
          <div className="flex items-center gap-2">
            <History className="h-4 w-4 text-indigo-600" />
            <CardTitle className="text-base font-semibold">Recent Compensation Changes</CardTitle>
          </div>
          <CardDescription>
            Audit log of salary increases, promotions, and corrections
          </CardDescription>
        </div>
        <Badge variant="outline" className="text-xs bg-amber-50 text-amber-700 border-amber-200">
          HR Restricted
        </Badge>
      </CardHeader>
      <CardContent>
        {changes.length === 0 ? (
          <div className="flex h-48 flex-col items-center justify-center text-center text-sm text-slate-400">
            <History className="h-8 w-8 text-slate-300 mb-2" />
            <p>No recent compensation modifications recorded</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-100 text-slate-400 font-medium">
                  <th className="pb-2.5 font-medium">Employee</th>
                  <th className="pb-2.5 font-medium">New Salary</th>
                  <th className="pb-2.5 font-medium">Effective Date</th>
                  <th className="pb-2.5 font-medium">Reason</th>
                  <th className="pb-2.5 font-medium">Authorized By</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {changes.map((c) => {
                  const hasOld = c.old_amount !== null && c.old_amount !== undefined;
                  const isIncrease = hasOld && Number(c.new_amount) > Number(c.old_amount);

                  return (
                    <tr key={c.id} className="hover:bg-slate-50/50 dark:hover:bg-slate-800/50">
                      <td className="py-2.5 pr-2">
                        <Link
                          href={`/employees/${c.employee_id}`}
                          className="font-medium text-indigo-600 hover:underline dark:text-indigo-400 block truncate max-w-[130px]"
                        >
                          {c.employee_name}
                        </Link>
                        <span className="text-[10px] text-slate-400">{c.employee_number}</span>
                      </td>

                      <td className="py-2.5 pr-2">
                        <div className="font-semibold text-slate-900 dark:text-white flex items-center gap-1">
                          {formatCurrency(c.new_amount, c.currency)}
                          {hasOld && isIncrease && (
                            <ArrowUpRight className="h-3 w-3 text-emerald-600 shrink-0" />
                          )}
                        </div>
                        {hasOld && (
                          <div className="text-[10px] text-slate-400">
                            was {formatCurrency(c.old_amount, c.currency)}
                          </div>
                        )}
                      </td>

                      <td className="py-2.5 pr-2 text-slate-600 dark:text-slate-300">
                        {formatDate(c.effective_from)}
                      </td>

                      <td className="py-2.5 pr-2">
                        <Badge
                          variant={c.is_correction ? "warning" : "secondary"}
                          className="text-[10px] py-0 px-1.5"
                        >
                          {c.change_reason.replace("_", " ")}
                        </Badge>
                      </td>

                      <td className="py-2.5 text-slate-500 text-[11px]">
                        {c.changed_by_name}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
