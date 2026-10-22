"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Users,
  FileSpreadsheet,
  LogOut,
  ShieldCheck,
  Building2,
  TrendingUp,
} from "lucide-react";
import { api, UserProfile } from "@/lib/api";
import { Button } from "@/components/ui/button";

export function Sidebar() {
  const pathname = usePathname();
  const [user, setUser] = useState<UserProfile | null>(null);

  useEffect(() => {
    api
      .getMe()
      .then(setUser)
      .catch(() => {});
  }, []);

  const navItems = [
    {
      label: "Dashboard",
      href: "/",
      icon: LayoutDashboard,
      active: pathname === "/",
    },
    {
      label: "Employee Directory",
      href: "/employees",
      icon: Users,
      active: pathname.startsWith("/employees"),
    },
  ];

  return (
    <aside className="fixed left-0 top-0 z-40 h-screen w-64 border-r border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900 flex flex-col justify-between">
      <div>
        {/* Brand Header */}
        <div className="flex h-16 items-center gap-3 border-b border-slate-100 px-6 dark:border-slate-800">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-600 text-white shadow-md shadow-indigo-500/20">
            <Building2 className="h-5 w-5" />
          </div>
          <div>
            <h1 className="font-bold text-slate-900 dark:text-white leading-tight">ACME Corp</h1>
            <p className="text-xs text-slate-500 dark:text-slate-400">Salary Management</p>
          </div>
        </div>

        {/* Navigation Links */}
        <div className="px-4 py-6">
          <p className="px-3 text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
            Operations
          </p>
          <nav className="space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                    item.active
                      ? "bg-indigo-50 text-indigo-700 font-semibold dark:bg-indigo-950/60 dark:text-indigo-400"
                      : "text-slate-600 hover:bg-slate-50 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-white"
                  }`}
                >
                  <Icon className={`h-4 w-4 ${item.active ? "text-indigo-600 dark:text-indigo-400" : ""}`} />
                  {item.label}
                </Link>
              );
            })}
          </nav>

          <p className="px-3 text-xs font-semibold uppercase tracking-wider text-slate-400 mt-8 mb-2">
            Reports & Export
          </p>
          <a
            href={api.getExportUrl()}
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-slate-600 hover:bg-slate-50 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-white transition-colors"
          >
            <FileSpreadsheet className="h-4 w-4 text-emerald-600" />
            Export Employees CSV
          </a>
        </div>
      </div>

      {/* User Footer */}
      <div className="border-t border-slate-100 p-4 dark:border-slate-800">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3 min-w-0">
            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-slate-100 font-semibold text-slate-700 dark:bg-slate-800 dark:text-slate-300">
              {user ? user.full_name[0] : "H"}
            </div>
            <div className="truncate">
              <p className="text-sm font-medium text-slate-900 dark:text-white truncate">
                {user ? user.full_name : "HR Manager"}
              </p>
              <div className="flex items-center gap-1 text-xs text-indigo-600 dark:text-indigo-400">
                <ShieldCheck className="h-3 w-3" />
                <span>Authorized HR</span>
              </div>
            </div>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => api.logout()}
            title="Log out"
            className="text-slate-400 hover:text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950"
          >
            <LogOut className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </aside>
  );
}
