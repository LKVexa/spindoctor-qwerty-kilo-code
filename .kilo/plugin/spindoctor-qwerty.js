// SpinDoctor Qwerty 1.1.0 - SpinDoctor Qwerty for Kilo Code: server plugin (6 tools)
// Copyright (C) 2026 RUSSELL PHILIP SMITHSON <russellsmithson77@outlook.com>
// SPDX-License-Identifier: GPL-3.0-or-later
// This program is free software: you can redistribute it and/or modify it under the terms of the GNU General
// Public License as published by the Free Software Foundation, either version 3 of the License, or (at your
// option) any later version. It is distributed WITHOUT ANY WARRANTY; see the LICENSE file for details.
//
// Kilo plugin (packages/kilo-docs/pages/automate/extending/plugins.md): default export { id, server }; the server function
// returns { tool: { name: tool({...}) } }. Each tool runs the bundled stdlib-only Python engine once
// (`spindoctor_cli.py tool NAME`, JSON on stdin, one JSON line on stdout). No hooks, no network, no dependencies of its own.
import { spawn, spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import path from "node:path";

const HERE = path.dirname(fileURLToPath(import.meta.url));
export const SKILL_DIR = path.resolve(HERE, "../skills/spindoctor-qwerty");
export const ENGINE_CLI = process.env.SPINDOCTOR_QWERTY_CLI || path.join(SKILL_DIR, "scripts", "spindoctor_cli.py");
export const VERSION = "1.1.0";

// Python: $SPINDOCTOR_PYTHON (a command, may include arguments such as "py -3"), else the first of these that runs Python 3.
const CANDIDATES = process.platform === "win32" ? [["py", "-3"], ["python"], ["python3"]] : [["python3"], ["python"]];
let PY = null;
export function python() {
  if (PY) return PY;
  if (process.env.SPINDOCTOR_PYTHON) return (PY = process.env.SPINDOCTOR_PYTHON.trim().split(/\s+/));
  for (const c of CANDIDATES) {
    try {
      const r = spawnSync(c[0], [...c.slice(1), "-c", "import sys; print(sys.version_info[0])"], { encoding: "utf8", windowsHide: true, timeout: 20000 });
      if (r.status === 0 && String(r.stdout).trim() === "3") return (PY = c);
    } catch { /* try the next one */ }
  }
  return (PY = CANDIDATES[0]);
}

const D = {
  run_script: "Run SpinDoctor q.* commands (one per line) in the persistent simulator workspace; returns results and TXT/JSON/CSV/PDF report paths. 1-298 logical qubits (59 per entangled factor). Classical FP64 simulation, not a quantum computer.",
  run_preset: "Run one of the 241 built-in SpinDoctor presets (qc-001..qc-241) with optional name=value overrides; returns per-step results and report paths.",
  list_presets: "List SpinDoctor presets (id, category, label, availability, commands); optional case-insensitive filter text.",
  report: "Show a SpinDoctor TXT report from the workspace, or list the newest reports when no name is given.",
  functions: "Return the in-chat Markdown table of every SpinDoctor function (Function | What it does | Command to type), grouped by family with runnable examples; section='presets' lists the 241 presets. Show it to the user verbatim on first use or when asked for help/functions. Read-only.",
  test_theory: "Test a theory with the SpinDoctor simulator and write a TXT+JSON+PDF theory report (hypothesis, script, raw results, verdict supported/not supported/inconclusive, limits). source='file' (absolute path of a txt/md/pdf/py/json/csv/q file), 'text' (pasted), or 'chat' (confirmed theory summary from the conversation + quoted excerpts and/or an exported chat transcript path). action='extract' reads the source; action='run' needs hypothesis, prediction, script and checks. The plugin cannot read chat history or attachments by itself.",
};

export function callEngine(name, args, cwd, timeoutMs = 600000) {
  return new Promise((resolve) => {
    let out = "", err = "", child;
    const [cmd, ...pre] = python();
    try {
      child = spawn(cmd, [...pre, ENGINE_CLI, "tool", name], { cwd: cwd || undefined, stdio: ["pipe", "pipe", "pipe"], windowsHide: true,
        env: { ...process.env, PYTHONUTF8: "1", PYTHONDONTWRITEBYTECODE: "1" } });
    } catch (e) { resolve({ ok: false, error: "Could not start Python (" + cmd + "): " + e.message + ". Set SPINDOCTOR_PYTHON." }); return; }
    const timer = setTimeout(() => child.kill(), timeoutMs);
    child.stdout.on("data", (d) => { out += d; });
    child.stderr.on("data", (d) => { err += d; });
    child.on("error", (e) => { clearTimeout(timer); resolve({ ok: false, error: "Python 3.8+ is required (set SPINDOCTOR_PYTHON): " + e.message }); });
    child.on("close", () => {
      clearTimeout(timer);
      const line = out.trim().split("\n").pop() || "";
      try { resolve(JSON.parse(line)); } catch { resolve({ ok: false, error: (err || out || "no output").slice(-2000) }); }
    });
    child.stdin.end(JSON.stringify(args || {}));
  });
}

export function asText(result) {
  if (result && result.ok && typeof result.markdown === "string") return result.markdown; // function table: show verbatim
  const s = JSON.stringify(result, null, 1);
  return s.length > 60000 ? s.slice(0, 60000) + "\n...[truncated; open the report files for full output]" : s;
}

// Argument shapes, written once against a zod-like builder `z` (Kilo's tool.schema is zod).
export function argShapes(z) {
  const ws = () => z.string().describe("Optional workspace folder (absolute path); default ~/spindoctor-workspace").optional();
  return {
    spindoctor_run_script: { script: z.string().describe("q.* commands, one per line"), workspace: ws() },
    spindoctor_run_preset: { preset_id: z.string().describe("Preset id, e.g. qc-061"), overrides: z.record(z.string(), z.string()).describe("Optional overrides (shots, basis, qubits, input, angle)").optional(), workspace: ws() },
    spindoctor_list_presets: { filter: z.string().describe("Optional filter text").optional() },
    spindoctor_report: { name: z.string().describe("Report file name; omit to list the newest").optional(), limit: z.number().int().optional(), workspace: ws() },
    spindoctor_functions: { section: z.enum(["commands", "gates", "tools", "presets", "all"]).optional(), filter: z.string().optional() },
    spindoctor_test_theory: { action: z.enum(["extract", "run"]).optional(), source: z.enum(["file", "text", "chat"]).optional(), path: z.string().optional(), text: z.string().optional(),
      excerpts: z.array(z.string()).optional(), hypothesis: z.string().optional(), prediction: z.string().optional(), checks: z.array(z.record(z.string(), z.any())).optional(),
      script: z.string().optional(), assumptions: z.array(z.string()).optional(), variables: z.array(z.string()).optional(), title: z.string().optional(), workspace: ws(), isolate: z.boolean().optional() },
  };
}
const DESC = { spindoctor_run_script: D.run_script, spindoctor_run_preset: D.run_preset, spindoctor_list_presets: D.list_presets,
  spindoctor_report: D.report, spindoctor_functions: D.functions, spindoctor_test_theory: D.test_theory };

export function buildTools(tool) {
  const shapes = argShapes(tool.schema), out = {};
  for (const [name, args] of Object.entries(shapes)) {
    out[name] = tool({ description: DESC[name], args, execute: async (a, ctx) => asText(await callEngine(name, a, ctx && ctx.directory)) });
  }
  return out;
}

// Without @kilocode/plugin (git-hosted installs: Kilo clones the repo and installs no dependencies) the same tools are registered as
// plain JSON-Schema definitions, which Kilo accepts for plugin tools but sends with every property listed as required. So optional
// fields are declared nullable, and nulls are dropped before the engine sees them.
export function jsonShapes() {
  const S = (d) => ({ type: "string", description: d }), N = (x) => ({ ...x, type: [x.type, "null"], description: (x.description || "") + " (null if unused)" });
  const ws = N(S("Optional workspace folder (absolute path); default ~/spindoctor-workspace"));
  const strs = (d) => N({ type: "array", items: { type: "string" }, description: d });
  return {
    spindoctor_run_script: { script: S("q.* commands, one per line"), workspace: ws },
    spindoctor_run_preset: { preset_id: S("Preset id, e.g. qc-061"), overrides: N({ type: "object", additionalProperties: { type: "string" }, description: "Optional overrides (shots, basis, qubits, input, angle)" }), workspace: ws },
    spindoctor_list_presets: { filter: N(S("Optional filter text")) },
    spindoctor_report: { name: N(S("Report file name; omit to list the newest")), limit: N({ type: "integer", description: "How many reports to list" }), workspace: ws },
    spindoctor_functions: { section: N({ type: "string", enum: ["commands", "gates", "tools", "presets", "all", null], description: "Section" }), filter: N(S("Filter text")) },
    spindoctor_test_theory: { action: N({ type: "string", enum: ["extract", "run", null], description: "extract or run" }), source: N({ type: "string", enum: ["file", "text", "chat", null], description: "file, text or chat" }),
      path: N(S("Absolute path of the theory file or chat export")), text: N(S("Pasted theory text or confirmed chat summary")), excerpts: strs("Quoted chat excerpts"),
      hypothesis: N(S("Hypothesis")), prediction: N(S("Measurable prediction")), checks: N({ type: "array", items: { type: "object" }, description: "Checks, e.g. {kind: probability, outcome: '11', expected: 0.5, tolerance: 0.05}" }),
      script: N(S("q.* script, one command per line")), assumptions: strs("Assumptions"), variables: strs("Variables"), title: N(S("Report title")), workspace: ws,
      isolate: N({ type: "boolean", description: "Run in a fresh simulator state" }) },
  };
}
const dropNulls = (a) => Object.fromEntries(Object.entries(a || {}).filter(([, v]) => v !== null && v !== undefined));

export function buildJsonTools() {
  const out = {};
  for (const [name, args] of Object.entries(jsonShapes())) {
    out[name] = { description: DESC[name], args, execute: async (a, ctx) => asText(await callEngine(name, dropNulls(a), ctx && ctx.directory)) };
  }
  return out;
}

const SpinDoctorQwerty = async () => {
  try {
    const { tool } = await import("@kilocode/plugin/tool");
    return { tool: buildTools(tool) }; // config-folder install: Kilo installs @kilocode/plugin there and finds skills/ itself
  } catch {
    // git-hosted install: the same 6 tools as plain JSON-Schema definitions. The bundled skill is not loaded in this mode (Kilo only
    // reads skills from config folders and trusted skills.paths); tools/install_kilo.py copies it into a config folder.
    return { tool: buildJsonTools() };
  }
};
export default { id: "spindoctor-qwerty", server: SpinDoctorQwerty };
