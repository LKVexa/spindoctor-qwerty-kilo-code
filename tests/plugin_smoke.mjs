// SpinDoctor Qwerty 1.1.0 - SpinDoctor Qwerty for Kilo Code: plugin smoke test (Node 18+, no dependencies)
// Copyright (C) 2026 RUSSELL PHILIP SMITHSON <russellsmithson77@outlook.com>
// SPDX-License-Identifier: GPL-3.0-or-later
// This program is free software: you can redistribute it and/or modify it under the terms of the GNU General
// Public License as published by the Free Software Foundation, either version 3 of the License, or (at your
// option) any later version. It is distributed WITHOUT ANY WARRANTY; see the LICENSE file for details.
//
//   node tests/plugin_smoke.mjs        -> one JSON line {ok, checks:[...]}
// Loads .kilo/plugin/spindoctor-qwerty.js the way Kilo does (default export {id, server}) without @kilocode/plugin, so it takes
// the JSON-Schema route, then runs two tools through the bundled engine. It also builds the zod route against a tiny stand-in
// builder to check that every tool gets a description and arguments. Nothing is written outside the system temp folder.
import { fileURLToPath, pathToFileURL } from "node:url";
import path from "node:path";
import os from "node:os";
import fs from "node:fs";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const mod = await import(pathToFileURL(path.join(ROOT, ".kilo", "plugin", "spindoctor-qwerty.js")).href);
const checks = []; const T = (name, ok, detail = "") => checks.push({ name, ok: !!ok, detail: String(detail).slice(0, 300) });
const NAMES = ["spindoctor_functions", "spindoctor_list_presets", "spindoctor_report", "spindoctor_run_preset", "spindoctor_run_script", "spindoctor_test_theory"];

T("default export is { id: 'spindoctor-qwerty', server: function }", mod.default && mod.default.id === "spindoctor-qwerty" && typeof mod.default.server === "function");
const hooks = await mod.default.server({ directory: os.tmpdir(), worktree: os.tmpdir() });
const names = Object.keys(hooks.tool || {}).sort();
T("without @kilocode/plugin the server returns the 6 tools (JSON-Schema route) and no other hooks", JSON.stringify(names) === JSON.stringify(NAMES) && Object.keys(hooks).join() === "tool", names);
T("every JSON-Schema tool has description, args and execute; optional fields are nullable",
  names.every((n) => hooks.tool[n].description && hooks.tool[n].args && typeof hooks.tool[n].execute === "function")
  && JSON.stringify(hooks.tool.spindoctor_run_script.args.workspace.type) === JSON.stringify(["string", "null"]));
const ws = fs.mkdtempSync(path.join(os.tmpdir(), "sdq_smoke_"));
const r1 = JSON.parse(await hooks.tool.spindoctor_run_preset.execute({ preset_id: "qc-001", overrides: null, workspace: ws }, { directory: ws }));
T("spindoctor_run_preset qc-001 through the engine (nulls dropped)", r1.ok === true, JSON.stringify(r1).slice(0, 200));
const md = await hooks.tool.spindoctor_functions.execute({ section: null, filter: null }, { directory: ws });
T("spindoctor_functions returns the Markdown table verbatim", md.includes("| Function | What it does | Command to type |"), md.slice(0, 120));
// zod route against a stand-in builder: records calls, so every tool must produce a shape
const chain = () => new Proxy(function () {}, { get: (t, k) => (k === "_zod" ? {} : chain), apply: () => chain() });
const fakeTool = Object.assign((def) => def, { schema: chain() });
const zt = mod.buildTools(fakeTool);
T("zod route (Kilo's @kilocode/plugin/tool) builds the same 6 tools", JSON.stringify(Object.keys(zt).sort()) === JSON.stringify(NAMES)
  && Object.values(zt).every((d) => d.description && Object.keys(d.args).length > 0));
fs.rmSync(ws, { recursive: true, force: true });
console.log(JSON.stringify({ ok: checks.every((c) => c.ok), checks }));
