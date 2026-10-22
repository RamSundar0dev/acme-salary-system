import { describe, it, expect } from "vitest";
import { formatCurrency, formatDate } from "@/lib/utils";

describe("Salary Formatting and Business Utilities", () => {
  it("formats positive USD amounts correctly", () => {
    expect(formatCurrency(125000, "USD")).toBe("$125,000");
  });

  it("formats positive EUR amounts correctly", () => {
    expect(formatCurrency(85000, "EUR")).toBe("€85,000");
  });

  it("formats positive GBP amounts correctly", () => {
    expect(formatCurrency(92000, "GBP")).toBe("£92,000");
  });

  it("handles null or undefined salary amounts safely", () => {
    expect(formatCurrency(null)).toBe("—");
    expect(formatCurrency(undefined)).toBe("—");
  });

  it("formats dates into readable human format", () => {
    const formatted = formatDate("2024-05-15");
    expect(formatted).toContain("May");
    expect(formatted).toContain("15");
    expect(formatted).toContain("2024");
  });

  it("handles null or empty dates gracefully", () => {
    expect(formatDate(null)).toBe("—");
    expect(formatDate(undefined)).toBe("—");
  });
});
