# Changelog

## 1.1.0 - 2026-10-11

- Engine 1.1.0 at parity with the updated SpinDoctor 3.1.2: 1-298 logical qubits (59 per entangled factor), the `mcx7` gate,
  wide-register Born-Z sampling, `q.folder` with 3.1.2 semantics, CSV report copies and measurement-CSV fitting equations. All 241
  presets replayed. Tools `spindoctor_functions` (function table, read-only) and `spindoctor_test_theory` (theory testing from a
  file, pasted text or the chat, with TXT+JSON+PDF theory reports). 1.0 described SpinDoctor 3.0.3 and a 29-qubit cap.
- **Checked against the real Kilo Code CLI (7.8.8).** The plugin module (`.kilo/plugin/spindoctor-qwerty.js`, default export
  `{ id, server }`) loads from a project `.kilo/` folder, the global `~/.config/kilo/` folder and a `git:` plugin spec; all 6 tools
  run through Kilo's tool registry.
- **Fixed: no tools from a git install.** 1.0 imported `@kilocode/plugin/tool` and silently returned no tools when it was missing.
  Kilo installs that package only in config folders; for `git:` plugins it installs no dependencies, so 1.0 registered nothing.
  1.1.0 falls back to plain JSON-Schema tool definitions (which Kilo accepts) with nullable optional fields, and drops nulls before
  the engine sees them.
- **Added the skill.** `.kilo/skills/spindoctor-qwerty/` (SKILL.md + the bundled engine, CLI, optional MCP server and examples)
  replaces 1.0's `.kilo/spindoctor-qwerty-engine/`. Kilo lists it in `<available_skills>` and loads it with the `skill` tool; when the
  tools are unavailable it tells Kilo to run the CLI with the bash tool from the skill's base directory.
- **Relative paths** (theory files, transcripts) now resolve against the session's project folder (the tool context's `directory`);
  1.0 used the Kilo process's working directory.
- **Python detection.** 1.0 ran `python` on Windows and `python3` elsewhere. 1.1.0 uses `$SPINDOCTOR_PYTHON` (may include arguments,
  e.g. `py -3`) or the first of `py -3` / `python` / `python3` (Windows) or `python3` / `python` that runs Python 3.
- `tools/install_kilo.py` copies only the plugin file and the skill into a project or the global config folder (and removes them
  with `--uninstall`), leaving other plugins and kilo.json alone. 1.0 said "copy the `.kilo/` folder into a project root".
- package.json: repo root is the package (`exports["./server"]` and `main`), license GPL-3.0-or-later, author, repository.
- SKILL.md examples use bundled files only (`examples/theory/xbasis.q`, new `examples/bell_theory_args.json`) and every one runs as
  written; frontmatter adds `compatibility` and `metadata`.
- Tests: `tests/kilo_host_check.py` (static checks and the real Kilo CLI with a local stand-in model), `tests/plugin_smoke.mjs`,
  `tests/stub_llm.py`.
- License changed from MIT to GPL-3.0-or-later. Author RUSSELL PHILIP SMITHSON. README, NOTICE, COPYRIGHT and SPDX headers added.

## 1.0.0

- First release: `.kilo/plugin/spindoctor-qwerty.js` and `.kilo/spindoctor-qwerty-engine/`, engine described as SpinDoctor 3.0.3.
