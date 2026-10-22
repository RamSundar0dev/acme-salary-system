import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { MetricCards } from "@/components/dashboard/MetricCards";
import { DashboardSummary } from "@/lib/api";

const mockSummary: DashboardSummary = {
  total_employees: 10000,
  active_employees: 9200,
  inactive_employees: 800,
  payroll_by_currency: [
    { currency: "USD", total_amount: 350000000, headcount: 3500 },
    { currency: "EUR", total_amount: 120000000, headcount: 1500 },
    { currency: "GBP", total_amount: 110000000, headcount: 1500 },
  ],
  metrics_by_country: [],
  metrics_by_department: [],
  recent_changes: [],
};

describe("MetricCards Component", () => {
  it("renders total, active, and inactive staff counts accurately", () => {
    render(
      <MetricCards
        summary={mockSummary}
        departments={[]}
        selectedCountry=""
        selectedDepartment=""
        selectedCurrency="USD"
        onFilterChange={vi.fn()}
      />
    );

    expect(screen.getByText("10,000")).toBeInTheDocument();
    expect(screen.getByText("9,200")).toBeInTheDocument();
    expect(screen.getByText("800")).toBeInTheDocument();
  });

  it("renders isolated payroll totals for each currency separately", () => {
    render(
      <MetricCards
        summary={mockSummary}
        departments={[]}
        selectedCountry=""
        selectedDepartment=""
        selectedCurrency="USD"
        onFilterChange={vi.fn()}
      />
    );

    expect(screen.getByText("USD")).toBeInTheDocument();
    expect(screen.getByText("EUR")).toBeInTheDocument();
    expect(screen.getByText("GBP")).toBeInTheDocument();
  });
});
