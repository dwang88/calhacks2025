import { AgentAction, AgentResult } from "@browserbasehq/stagehand";
import { exec } from "child_process";
import fs from "fs/promises";

export async function replay(result: AgentResult) {
  const history = result.actions;
  const replay = history
    .map((action: AgentAction) => {
      switch (action.type) {
        case "act":
          if (!action.playwrightArguments) {
            throw new Error("No playwright arguments provided");
          }
          return `await page.act(${JSON.stringify(
            action.playwrightArguments
          )})`;
        case "extract":
          return `await page.extract("${action.parameters}")`;
        case "goto":
          return `await page.goto("${action.parameters}")`;
        case "wait":
          return `await page.waitForTimeout(${parseInt(
            action.parameters as string
          )})`;
        case "navback":
          return `await page.goBack()`;
        case "refresh":
          return `await page.reload()`;
        case "close":
          return `await stagehand.close()`;
        default:
          return `await stagehand.oops()`;
      }
    })
    .join("\n");

  console.log("Replay:");
  const boilerplate = `
import { Page, BrowserContext, Stagehand } from "@browserbasehq/stagehand";

export async function main(stagehand: Stagehand) {
    const page = stagehand.page
	${replay}
}
  `;
  await fs.writeFile("replay.ts", boilerplate);

  // Format the replay file with prettier
  await new Promise((resolve, reject) => {
    exec(
      "npx prettier --write replay.ts",
      (error: any, stdout: any, stderr: any) => {
        if (error) {
          console.error(`Error formatting replay.ts: ${error}`);
          reject(error);
          return;
        }
        resolve(stdout);
      }
    );
  });
}