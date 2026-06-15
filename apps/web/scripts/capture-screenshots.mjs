import { mkdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { chromium, expect } from "@playwright/test";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, "../../..");
const outputDir = path.join(repoRoot, "docs/assets");
const baseUrl = process.env.PLAYWRIGHT_BASE_URL ?? "http://localhost:3000";
const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
const sampleAgentUrl = process.env.ARW_SAMPLE_AGENT_URL ?? "http://localhost:9000/agent";
const sampleAgentHealthUrl =
  process.env.ARW_SAMPLE_AGENT_HEALTH_URL ?? "http://localhost:9000/health";
const sampleAgentName = "Local Sample HTTP Agent";
const comparisonWarmupRuns = Number(process.env.ARW_SCREENSHOT_COMPARISON_RUNS ?? "4");

async function capture(locator, name) {
  await locator.scrollIntoViewIfNeeded();
  await locator.screenshot({
    path: path.join(outputDir, name),
    animations: "disabled"
  });
}

async function fetchJson(url, options) {
  const response = await fetch(url, options);
  const body = await response.json().catch(() => null);
  if (!response.ok) {
    throw new Error(`${url} returned HTTP ${response.status}: ${JSON.stringify(body)}`);
  }
  return body;
}

async function ensureSampleAgentTarget() {
  await fetchJson(sampleAgentHealthUrl);

  const targets = await fetchJson(`${apiBaseUrl}/agent-targets`);
  const existing = targets.find(
    (target) =>
      target.name === sampleAgentName &&
      target.agent_type === "http_json" &&
      target.endpoint_url === sampleAgentUrl
  );
  if (existing) {
    return existing;
  }

  return fetchJson(`${apiBaseUrl}/agent-targets`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      name: sampleAgentName,
      agent_type: "http_json",
      endpoint_url: sampleAgentUrl,
      auth_type: "none",
      version: "v1",
      description: "Deterministic local external agent for public ARW benchmark demos."
    })
  });
}

async function warmupExternalEvalComparison(targetId) {
  for (let index = 0; index < comparisonWarmupRuns; index += 1) {
    await fetchJson(`${apiBaseUrl}/evals/run`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        prompt_version: "v1",
        agent_target_id: targetId
      })
    });
  }
}

async function main() {
  await mkdir(outputDir, { recursive: true });
  const sampleTarget = await ensureSampleAgentTarget();
  await warmupExternalEvalComparison(sampleTarget.id);

  const browser = await chromium.launch();
  const page = await browser.newPage({
    viewport: { width: 1440, height: 1200 },
    deviceScaleFactor: 1
  });

  try {
    await page.goto(baseUrl, { waitUntil: "networkidle" });

    const sampleTargetCard = page.locator("article").filter({ hasText: sampleAgentName }).first();
    await expect(sampleTargetCard).toContainText(sampleAgentUrl, { timeout: 30_000 });
    await sampleTargetCard.getByRole("button", { name: "Use for Benchmark" }).click();
    await sampleTargetCard.getByRole("button", { name: "Test Connection" }).click();
    await expect(sampleTargetCard).toContainText("Connection test passed", { timeout: 30_000 });

    await capture(page.locator("#run-agent"), "dashboard.png");
    await capture(page.locator("#agent-targets"), "agent-targets.png");

    await page.locator("#run-agent").getByRole("button", { name: "Run Agent" }).click();
    await expect(page.locator("#review")).toContainText("Run ID:", { timeout: 90_000 });
    await expect(page.locator("#traces")).toContainText("Run Trace", { timeout: 30_000 });
    await capture(page.locator("#traces"), "trace-viewer.png");

    await expect(page.locator("#evals")).toContainText(sampleAgentName, { timeout: 30_000 });
    await page.locator("#evals").getByRole("button", { name: "Run Evals" }).click();
    await expect(page.locator("#evals")).toContainText("Total", { timeout: 120_000 });
    await expect(page.locator("#evals")).toContainText(`Agent Under Test: ${sampleAgentName}`, {
      timeout: 30_000
    });
    await expect(page.locator("#evals")).toContainText("Failed", { timeout: 30_000 });
    await capture(page.locator("#evals"), "eval-runner.png");

    await expect(page.locator("#compare")).toContainText("Eval #", { timeout: 30_000 });
    await capture(page.locator("#compare"), "eval-comparison.png");
  } finally {
    await browser.close();
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
