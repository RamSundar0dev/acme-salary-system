"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { Building2, Shield, Lock, Mail, AlertCircle, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { api } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("hr.manager@acme.corp");
  const [password, setPassword] = useState("AcmeHR2026!SecurePass");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await api.login(email, password);
      router.push("/");
    } catch (err: any) {
      setError(err.message || "Failed to authenticate. Please check your credentials.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-slate-50 px-4 py-12 dark:bg-slate-950">
      <div className="w-full max-w-md space-y-8">
        {/* Brand Header */}
        <div className="text-center">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-indigo-600 text-white shadow-xl shadow-indigo-500/25">
            <Building2 className="h-8 w-8" />
          </div>
          <h2 className="mt-6 text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
            ACME Salary Management
          </h2>
          <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
            Sign in with authorized HR Manager credentials
          </p>
        </div>

        {/* Login Card */}
        <div className="rounded-2xl border border-slate-200 bg-white p-8 shadow-xl shadow-slate-200/50 dark:border-slate-800 dark:bg-slate-900 dark:shadow-none">
          {error && (
            <div className="mb-6 flex items-start gap-3 rounded-lg border border-rose-200 bg-rose-50 p-3 text-xs text-rose-800 dark:border-rose-900 dark:bg-rose-950 dark:text-rose-300">
              <AlertCircle className="h-4 w-4 shrink-0 text-rose-600 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-5">
            <div>
              <label className="text-xs font-semibold text-slate-700 dark:text-slate-300">
                Work Email
              </label>
              <div className="relative mt-1">
                <Mail className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
                <Input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="hr.manager@acme.corp"
                  className="pl-9 h-10"
                />
              </div>
            </div>

            <div>
              <label className="text-xs font-semibold text-slate-700 dark:text-slate-300">
                Password
              </label>
              <div className="relative mt-1">
                <Lock className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
                <Input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  className="pl-9 h-10"
                />
              </div>
            </div>

            <Button
              type="submit"
              disabled={loading}
              className="w-full h-10 bg-indigo-600 hover:bg-indigo-700 text-white font-medium shadow-md shadow-indigo-600/20 gap-2"
            >
              <span>{loading ? "Authenticating..." : "Sign In to HR Portal"}</span>
              <ArrowRight className="h-4 w-4" />
            </Button>
          </form>

          {/* Demo Credentials Box */}
          <div className="mt-6 rounded-lg border border-indigo-100 bg-indigo-50/60 p-3 dark:border-indigo-900/40 dark:bg-indigo-950/30">
            <div className="flex items-center gap-1.5 text-xs font-semibold text-indigo-900 dark:text-indigo-300">
              <Shield className="h-3.5 w-3.5 text-indigo-600" />
              <span>Incubyte Assessment Demo Account:</span>
            </div>
            <div className="mt-1 text-[11px] text-indigo-700/90 dark:text-indigo-400 font-mono space-y-0.5">
              <div>Email: <strong>hr.manager@acme.corp</strong></div>
              <div>Pass: <strong>AcmeHR2026!SecurePass</strong></div>
            </div>
          </div>
        </div>

        <p className="text-center text-xs text-slate-400">
          Secured with JWT authentication, bcrypt hashing, and PostgreSQL audit trail.
        </p>
      </div>
    </div>
  );
}
