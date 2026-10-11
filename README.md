# SpinDoctor Qwerty for Kilo Code

A [Kilo Code](https://github.com/Kilo-Org/kilocode) plugin and skill that runs the **SpinDoctor 3.1.2 quantum-circuit simulator** on
your computer: `q.*` circuit scripts (1-298 logical qubits), the 241 built-in presets, folders of command files (`q.folder`), and
theory tests from a file, pasted text or the chat itself, each with TXT, PDF, JSON and CSV reports. It adds 6 tools to Kilo's agent
and a `spindoctor-qwerty` skill.

> **Honest limits.** SpinDoctor is a classical FP64 simulator. It is not a quantum computer, does not connect to quantum hardware,
> and gives no quantum speed-up or advantage. One entangled group is limited to 59 qubits and dense groups are limited by memory
> (2^n x 16 bytes). Registers wider than 29 qubits sample in basis Z only. Histograms are seeded Born samples.

Version 1.1.0 - engine 1.1.0 (SpinDoctor 3.1.2 parity) - tested with the Kilo Code CLI 7.8.8 - Node 18+ (Kilo's runtime) and
Python 3.8+, standard library only - no network, no account and no keys for the plugin itself.

## Install

Pick one. Start a new Kilo session afterwards.

**One project** (recommended; tools + skill):

```bash
git clone https://github.com/LKVexa/spindoctor-qwerty-kilo-code
python3 spindoctor-qwerty-kilo-code/tools/install_kilo.py /path/to/your/project
```

**Every project** (tools + skill in `~/.config/kilo/`):

```bash
python3 spindoctor-qwerty-kilo-code/tools/install_kilo.py --global
```

`install_kilo.py` copies only `plugin/spindoctor-qwerty.js` and `skills/spindoctor-qwerty/` into the chosen `.kilo/` or
`~/.config/kilo/` folder, merging with whatever is there; `--uninstall` removes just those two. Kilo then loads every `.js` file in
`plugin/` and every `skills/*/SKILL.md` on startup, and installs its own `@kilocode/plugin` package into that folder (that needs npm
access once; if that install fails, the plugin registers the JSON-Schema form of its tools described below). On Windows use `py -3` or `python` instead of `python3`.

**From GitHub without cloning** (tools only): add the plugin to `kilo.json` in your project (or `~/.config/kilo/kilo.json`):

```json
{ "$schema": "https://app.kilo.ai/config.json", "plugin": ["git:github.com/LKVexa/spindoctor-qwerty-kilo-code"] }
```

Kilo clones the repo into its cache and loads the package.json `./server` entry. Two differences from the folder install: Kilo
installs no dependencies for git plugins, so the tools are registered as plain JSON-Schema definitions whose optional fields are
sent as nullable (the model may pass `null`; the plugin drops nulls), and the skill is not loaded (Kilo reads skills only from
config folders and trusted `skills.paths`). Pin a tag or commit with `git:github.com/LKVexa/spindoctor-qwerty-kilo-code@<ref>`.

Python: the plugin uses `$SPINDOCTOR_PYTHON` if set (a command, arguments allowed, e.g. `py -3`), otherwise the first of `py -3`,
`python`, `python3` (Windows) or `python3`, `python` (elsewhere) that runs Python 3.

## What's in the repo

| Path | What it is |
|---|---|
| `package.json` | Package manifest: `exports["./server"]` and `main` -> `.kilo/plugin/spindoctor-qwerty.js`, GPL-3.0-or-later |
| `.kilo/plugin/spindoctor-qwerty.js` | The server plugin: default export `{ id: "spindoctor-qwerty", server }`, 6 tools, no hooks, no network |
| `.kilo/skills/spindoctor-qwerty/` | Skill (`SKILL.md`), the bundled engine (`spindoctor/`), CLI and optional MCP server (`scripts/`), examples, LICENSE |
| `tools/install_kilo.py` | Copies (or `--uninstall`s) the plugin and skill into a project or the global config folder |
| `FUNCTIONS.md` | The full function table with a runnable example for every command |
| `tests/` | Host check, plugin smoke test, shared end-to-end suite, local OpenAI-compatible stand-in, reference outputs |

Because the repo root has a `.kilo/` folder, running Kilo inside a clone of this repo also loads the plugin and skill.

Each tool call starts `spindoctor_cli.py tool <name>` once (JSON in, one JSON line out) with the session's project folder as the
working directory, so relative paths resolve there. Reports and state go to `~/spindoctor-workspace` unless a call passes
`workspace`; nothing is written into the plugin folder. The same engine also ships an MCP server
(`.kilo/skills/spindoctor-qwerty/scripts/spindoctor_mcp.py`) if you prefer Kilo's `mcp` config; you do not need both.

## Using it

- Ask in plain language: "show the SpinDoctor functions", "run a 3-qubit GHZ circuit", "test the theory we discussed".
- Tools: `spindoctor_functions`, `spindoctor_run_script`, `spindoctor_run_preset`, `spindoctor_list_presets`, `spindoctor_report`,
  `spindoctor_test_theory`. The `bash` fallback follows your bash permission settings.
- The skill appears in Kilo's `<available_skills>`; when loaded, Kilo prints its base directory, and SKILL.md's CLI examples
  (`python3 scripts/spindoctor_cli.py functions` ...) run from there.

## SpinDoctor Qwerty - plugin tools

| Function | What it does | Command to type |
|---|---|---|
| Function table (spindoctor_functions) | Show this table in chat | Ask: "show the SpinDoctor functions" |
| Run a script (spindoctor_run_script) | Run any q.* lines above; returns results + TXT/JSON/CSV/PDF report paths | Ask: "run q.circuit new bell 2 / q.circuit add h 0 / ..." |
| Run a preset (spindoctor_run_preset) | Run qc-001..qc-241 with overrides | Ask: "run preset qc-067 with shots=64" |
| List presets (spindoctor_list_presets) | Search the 241 presets | Ask: "list presets about Grover" |
| Read a report (spindoctor_report) | List/read TXT reports (PDF/JSON paths alongside) | Ask: "show the newest SpinDoctor report" |
| Test a theory from a file (spindoctor_test_theory source=file) | Read a .txt/.md/.pdf/.py/.json/.csv/.q attachment, then hypothesis -> prediction -> q.* script -> run -> verdict + TXT/PDF theory report | Ask: "test the theory in C:/notes/theory.md" (the host must pass the file path/content) |
| Test a theory from text (spindoctor_test_theory source=text) | Same pipeline for pasted text | Ask: "test this theory: a Hadamard on \|0> gives 50/50" |
| Test the theory we discussed (spindoctor_test_theory source=chat) | The AI summarises the theory from the conversation (claims, assumptions, variables, prediction), you confirm, then it is tested; quoted excerpts go in the report under 'Source: chat history'. An exported chat transcript (.txt/.md/.json/.html) also works | Ask: "test the theory we discussed" or "test the theory in my exported chat C:/chats/conversation.json" |

Every command family is listed with a runnable example in **[FUNCTIONS.md](FUNCTIONS.md)** (the exact table the tool shows):
circuits (`q.circuit`, including 298-qubit wide registers and the `mcx7` gate), queries (`q.query`), the tranche register
(`q.tranche`), the procedural grid, presets and sequences, resource planning, math calculators, physics models, lessons, noise, error
correction, compilation, algorithms, inputs/folders/history (`q.input`, `q.folder`, `q.history`) and the cartridge commands.

## Theory testing

`spindoctor_test_theory` turns a claim into a test: hypothesis -> measurable prediction -> `q.*` script -> run -> compare -> a TXT +
JSON + PDF **theory test report** with the hypothesis, script, raw results, verdict (*supported*, *not supported* or *inconclusive*)
and limits.

- **From a file:** .txt, .md, .pdf, .py, .json, .csv or .q. In Kilo, give the file's path (relative to the project folder, or absolute) or paste the text.
- **From pasted text.**
- **From the chat history:** say *"test the theory we discussed"*. The model writes a short summary (claims, assumptions, variables,
  measurable prediction), shows it to you to confirm or correct, then passes it with optional quoted excerpts; the report records them
  under *Source: chat history*. Exported chat transcripts (.txt/.md/.json/.html from ChatGPT, Claude and others) also work.
- The plugin cannot read your conversation or attachments by itself: only the model sees them, and very long conversations may already
  be truncated by the context window.

Sample theory files and chat transcripts are in `.kilo/skills/spindoctor-qwerty/examples/theory/`. The two sample
PDFs are stored as text; run `python3 skills/spindoctor-qwerty/examples/theory/make_sample_pdfs.py` to
recreate them.

## Folder ingestion (`q.folder`)

`q.folder run path="<folder>"` runs every supported file at the top level of a folder (.txt, .csv, .json, .qasm, .qasm2, .circuit,
.pdf) in ordinal name order: 1-128 supported files, at most 4 MiB per file, 1-128 commands per file and 4096 characters per command,
strict UTF-8. Other files (for example .md) are skipped and listed. The first failing file stops the job.


## Testing

| Test | Command |
|---|---|
| Static checks + plugin smoke test | `python3 tests/kilo_host_check.py` |
| Real Kilo Code CLI | `python3 tests/kilo_host_check.py --kilo "$(command -v kilo)"` (add `--source github.com/LKVexa/spindoctor-qwerty-kilo-code` for the git route from GitHub) |
| Plugin smoke test only | `node tests/plugin_smoke.mjs` |
| End-to-end suite only | `python3 tests/e2e_mcp.py --server python3 .kilo/skills/spindoctor-qwerty/scripts/spindoctor_mcp.py --examples .kilo/skills/spindoctor-qwerty/examples/theory` |

**Real host, scripted model.** The host check uses the real Kilo Code CLI (`@kilocode/cli` 7.8.8 from npm, MIT) with throwaway
HOME/XDG folders and no Kilo account: one-shot `kilo run ... --format json` sessions with a custom `stub` provider pointing at
`tests/stub_llm.py`, a local scripted stand-in for an OpenAI-compatible endpoint on 127.0.0.1 (placeholder key). Through Kilo's own
plugin loader and tool registry it runs the 6 tools from a project install (function table, a Bell circuit, qc-001, a relative theory
path, a theory from the chat: verdict *supported*, PDF written), loads the skill and runs the CLI through the bash tool, then checks
the global install and its uninstall, the `git:` route, and the shared end-to-end suite. Not tested: a real model choosing the tools,
the interactive TUI, the VS Code extension, Windows, macOS. Results: [E2E_RESULTS.md](E2E_RESULTS.md).

## Author and license

Author: **RUSSELL PHILIP SMITHSON** <russellsmithson77@outlook.com>

Copyright (C) 2026 RUSSELL PHILIP SMITHSON. Licensed under the GNU General Public License v3.0 or later (`GPL-3.0-or-later`): see
[LICENSE](LICENSE), [NOTICE](NOTICE) and [COPYRIGHT](COPYRIGHT). Kilo Code is a Kilo-Org project; this plugin is not affiliated with
Kilo Code.
