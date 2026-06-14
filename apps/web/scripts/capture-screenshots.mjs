import { mkdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { chromium, expect } from "@playwright/test";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, "../../..");
const outputDir = path.join(repoRoot, "docs/assets");
const baseUrl = process.env.PLAYWRIGHT_BASE_URL ?? "http://localhost:3000";

async function capture(locator, name) {
  await locator.scrollIntoViewIfNeeded();
  await locator.screenshot({
    path: path.join(outputDir, name),
    animations: "disabled"
  });
}

async function main() {
  await mkdir(outputDir, { recursive: true });

  const browser = await chromium.launch();
  const page = await browser.newPage({
    viewport: { width: 1440, height: 1200 },
    deviceScaleFactor: 1
  });

  try {
    await page.goto(baseUrl, { waitUntil: "networkidle" });

    await capture(page.locator("#run-agent"), "dashboard.png");
    await capture(page.locator("#agent-targets"), "agent-targets.png");

    await page.locator("#run-agent").getByRole("button", { name: "Run Agent" }).click();
    await expect(page.locator("#review")).toContainText("Run ID:", { timeout: 90_000 });
    await expect(page.locator("#traces")).toContainText("Run Trace", { timeout: 30_000 });
    await capture(page.locator("#traces"), "trace-viewer.png");

    await page.locator("#evals").getByRole("button", { name: "Run Evals" }).click();
    await expect(page.locator("#evals")).toContainText("Total", { timeout: 120_000 });
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
