"use client";

import React from "react";
import { Database, Shield, Calendar } from "lucide-react";
import { Badge } from "@/components/ui/badge";

export function Navbar({ title, description }: { title: string; description?: string }) {
  const currentDate = new Date().toLocaleDateString("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
    year: "numeric",
  });

  return (
    <header className="sticky top-0 z-30 flex h-16 w-full items-center justify-between border-b border-slate-200 bg-white/80 px-8 backdrop-blur-md dark:border-slate-800 dark:bg-slate-900/80">
      <div>
        <h2 className="text-lg font-bold text-slate-900 dark:text-white leading-tight">
          {title}
        </h2>
        {description && (
          <p className="text-xs text-slate-500 dark:text-slate-400">{description}</p>
        )}
      </div>

      <div className="flex items-center gap-4">
        {/* System status pill */}
        <div className="hidden sm:flex items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50/60 px-3 py-1 text-xs font-medium text-emerald-800 dark:border-emerald-800/40 dark:bg-emerald-950/40 dark:text-emerald-300">
          <Database className="h-3 w-3 text-emerald-600 animate-pulse" />
          <span>PostgreSQL 16 • 10,000 Records</span>
        </div>

        <div className="hidden md:flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400">
          <Calendar className="h-3.5 w-3.5 text-slate-400" />
          <span>{currentDate}</span>
        </div>

        <Badge variant="outline" className="border-indigo-200 bg-indigo-50/50 text-indigo-700 dark:border-indigo-800/60 dark:bg-indigo-950/40 dark:text-indigo-300 gap-1 py-1">
          <Shield className="h-3 w-3 text-indigo-500" />
          <span>HR Manager</span>
        </Badge>
      </div>
    </header>
  );
}
