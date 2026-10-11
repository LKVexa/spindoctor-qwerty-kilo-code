# E2E results - spindoctor-qwerty-kilo-code 1.1.0

Host: **real Kilo Code CLI 7.8.8** (`@kilocode/cli` from npm) with throwaway HOME/XDG folders and no Kilo account. Model turns come
from `tests/stub_llm.py`, a local scripted stand-in for an OpenAI-compatible endpoint on 127.0.0.1 (a custom `stub` provider with a
placeholder key), so tool calls are scripted; everything between the model and the engine (config-folder and `git:` plugin loading,
Kilo's `@kilocode/plugin` install, the tool registry and its schemas, the session's project directory, skill discovery and the `skill`
tool, the bash tool) is the real Kilo. Python 3.13.5 for the checks.

Not tested: a real model choosing the tools by itself, the interactive TUI, the VS Code extension, Windows, macOS.

## Host check: 28/28

| Result | Check |
|---|---|
| PASS | package.json: version 1.1.0, GPL-3.0-or-later, author, type module, exports ./server and main -> .kilo/plugin/spindoctor-qwerty.js |
| PASS | plugin module: SPDX header, `node --check` passes, default export {id, server}, no network or hooks besides `tool` |
| PASS | SKILL.md: name spindoctor-qwerty = folder, compatibility, metadata version 1.1.0, GPL-3.0-or-later, guardrail, no other host variables |
| PASS | every .py/.js/.mjs file has a GPL-3.0-or-later SPDX header (29 files) |
| PASS | tools/install_kilo.py --help documents project, --global and --uninstall |
| PASS | every CLI command in SKILL.md runs as written from the skill folder (6 commands, bundled files only) |
| PASS | optional MCP server (scripts/spindoctor_mcp.py) answers initialize |
| PASS | tests/plugin_smoke.mjs: module shape, JSON-Schema route (6 tools, nullable optionals, qc-001, function table), zod route |
| PASS | Kilo Code CLI runs: kilo 7.8.8 |
| PASS | tools/install_kilo.py PROJECT copies plugin + skill into PROJECT/.kilo/ |
| PASS | project route: kilo run exits 0 and the session offers the 6 tools + skill + bash |
| PASS | project route uses the zod schemas (Kilo installed @kilocode/plugin in .kilo/): run_script requires only `script` |
| PASS | skill listed in the system prompt (<available_skills> spindoctor-qwerty) |
| PASS | spindoctor_functions: the Markdown function table verbatim |
| PASS | spindoctor_run_script: Bell circuit ok |
| PASS | spindoctor_run_preset qc-001 ok |
| PASS | relative path `my_theory.txt` resolves against the session's project folder (theory extract ok) |
| PASS | spindoctor_test_theory from the chat: supported, 2 excerpts, valid PDF under ~/spindoctor-workspace |
| PASS | skill tool loads SKILL.md with Kilo's base directory = the installed skill folder |
| PASS | bash fallback: the CLI from the skill's base directory runs preset qc-002 |
| PASS | tools/install_kilo.py --global copies plugin + skill into $XDG_CONFIG_HOME/kilo/ |
| PASS | global route: a fresh project gets the 6 tools and the skill; list_presets ghz ok |
| PASS | --uninstall --global: the next session has no SpinDoctor tools or skill |
| PASS | git route (`plugin: ["repo"]`): Kilo clones it and registers the 6 tools |
| PASS | git route uses the JSON-Schema definitions (no dependencies installed): workspace is nullable |
| PASS | git route: Bell circuit and qc-003 ok with null optionals |
| PASS | git route: the skill is not loaded (documented; install_kilo.py adds it) |
| PASS | shared end-to-end suite through the bundled MCP server: SUMMARY 12/12 passed in 13.0s |

## Shared end-to-end suite: 12/12

Started with the bundled MCP server: `python3 .kilo/skills/spindoctor-qwerty/scripts/spindoctor_mcp.py` (same engine the plugin tools call).

| Result | Check |
|---|---|
| PASS | initialize (server spindoctor-qwerty 1.1.0) |
| PASS | tools/list exposes the 6 tools |
| PASS | function table (Markdown, 19 sections, 298-qubit limits listed) |
| PASS | 241 presets listed |
| PASS | one script per command family (16 families, every table example) |
| PASS | 298-qubit circuit with mcx7 (prepared-factor-Born-Z) |
| PASS | q.folder on mixed .txt/.csv/.json/.qasm folder (+ .md skipped) |
| PASS | theory from a file -> supported, TXT+PDF report |
| PASS | theory from a chat summary + quoted excerpts -> supported |
| PASS | theory from an exported chat transcript -> supported |
| PASS | presets qc-001..qc-025 match the updated 3.1.2 reference (20 identical, 5 documented differences) |
| PASS | TXT+PDF reports valid (255 PDFs, 255 TXT twins) |

## Runs

- Pre-push (box, 2026-10-11): host check 28/28 with the real Kilo CLI 7.8.8; git route from a local git copy of the staged repo.
