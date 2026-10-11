#!/usr/bin/env python3
# SpinDoctor Qwerty 1.1.0 - SpinDoctor Qwerty for Kilo Code: host check
# Copyright (C) 2026 RUSSELL PHILIP SMITHSON <russellsmithson77@outlook.com>
# SPDX-License-Identifier: GPL-3.0-or-later
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version. It is distributed WITHOUT ANY WARRANTY; see the LICENSE file for details.
"""Run from the repo root:

  python3 tests/kilo_host_check.py                                    # static checks + plugin smoke test (Node 18+)
  python3 tests/kilo_host_check.py --kilo "$(command -v kilo)"         # + the real Kilo Code CLI
  python3 tests/kilo_host_check.py --kilo ... --source github.com/LKVexa/spindoctor-qwerty-kilo-code   # git route from GitHub

Static: package.json, the plugin module, SKILL.md, licence headers, tools/install_kilo.py, every CLI command in SKILL.md, the
optional MCP server's `initialize`, and tests/plugin_smoke.mjs.
--kilo: with a throwaway HOME/XDG folders, the real Kilo CLI runs one-shot `kilo run ... --format json` sessions against
tests/stub_llm.py, a local scripted stand-in for an OpenAI-compatible endpoint on 127.0.0.1 (a custom `stub` provider with a
placeholder key in the throwaway global kilo.json: no Kilo account, nothing leaves the machine except Kilo's own npm install of
@kilocode/plugin and the provider SDK). Three install routes: project `.kilo/` (tools/install_kilo.py PROJECT), global
`~/.config/kilo/` (--global), and a `git:` plugin spec (a local git copy of this repo, or --source). Covers the 6 tools, a chat
theory with its PDF, a relative path resolved against the project, the skill tool and the bash fallback, uninstall, and the shared
end-to-end suite through the bundled MCP server. Standard library only.
"""
import json, os, re, shutil, socket, subprocess, sys, tempfile, time
sys.dont_write_bytecode = True; os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
SK = os.path.join(ROOT, ".kilo", "skills", "spindoctor-qwerty"); PLUGIN = os.path.join(ROOT, ".kilo", "plugin", "spindoctor-qwerty.js")
INSTALL = os.path.join(ROOT, "tools", "install_kilo.py")
TOOLS = ["spindoctor_functions", "spindoctor_list_presets", "spindoctor_report", "spindoctor_run_preset", "spindoctor_run_script", "spindoctor_test_theory"]
R = []
OK = lambda s: bool(re.search(r'"ok":\s*true', s or ""))
BELL = "q.circuit new bell 2\nq.circuit add h 0\nq.circuit add cx 0 1\nq.circuit run shots 1000 basis z"


def T(name, ok, detail=""):
    R.append({"check": name, "pass": bool(ok), "detail": str(detail)[:600]})
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else "  -- " + str(detail)[:500])); sys.stdout.flush()


def static():
    p = json.load(open(os.path.join(ROOT, "package.json"), encoding="utf-8"))
    T("package.json: version 1.1.0, GPL-3.0-or-later, author, type module, exports ./server and main -> .kilo/plugin/spindoctor-qwerty.js",
      p.get("version") == "1.1.0" and p.get("license") == "GPL-3.0-or-later" and "RUSSELL PHILIP SMITHSON" in p.get("author", "") and p.get("type") == "module"
      and p.get("exports", {}).get("./server", {}).get("import") == "./.kilo/plugin/spindoctor-qwerty.js" and p.get("main") == "./.kilo/plugin/spindoctor-qwerty.js", p)
    js = open(PLUGIN, encoding="utf-8").read()
    T("plugin module: SPDX header, `node --check` passes, default export {id, server}, no network or hooks besides `tool`",
      "SPDX-License-Identifier: GPL-3.0-or-later" in js[:400] and subprocess.run(["node", "--check", PLUGIN]).returncode == 0
      and 'export default { id: "spindoctor-qwerty", server: SpinDoctorQwerty }' in js and not re.search(r"\bfetch\(|https?://", js))
    t = open(os.path.join(SK, "SKILL.md"), encoding="utf-8").read(); fm = t.split("---")[1]
    T("SKILL.md: name spindoctor-qwerty = folder, compatibility, metadata version 1.1.0, GPL-3.0-or-later, guardrail, no other host variables",
      "\nname: spindoctor-qwerty\n" in fm and "compatibility:" in fm and 'version: "1.1.0"' in fm and "license: GPL-3.0-or-later" in fm
      and "not a\nquantum computer" in t and not re.search(r"\$\{[A-Z]+_PLUGIN_ROOT\}", t))
    py = [os.path.join(d, f) for d, _, fs in os.walk(ROOT) if "/.git" not in d and "node_modules" not in d and "__pycache__" not in d for f in fs if f.endswith((".py", ".js", ".mjs"))]
    bad = [x for x in py if "SPDX-License-Identifier: GPL-3.0-or-later" not in open(x, encoding="utf-8").read(2500)]
    T("every .py/.js/.mjs file has a GPL-3.0-or-later SPDX header (%d files)" % len(py), not bad, bad[:3])
    o = subprocess.run([sys.executable, INSTALL, "--help"], capture_output=True, text=True).stdout
    T("tools/install_kilo.py --help documents project, --global and --uninstall", "--global" in o and "--uninstall" in o)
    cmds = [ln.split("  #")[0].strip() for blk in re.findall(r"```bash\n(.*?)```", t, re.S) for ln in blk.splitlines() if ln.startswith("python3 scripts/")]
    ws = tempfile.mkdtemp(prefix="sdq_cli_"); bad = []
    for c in cmds:
        argv = c.split(" ", 2); rest = re.findall(r'"[^"]*"|\S+', argv[2])
        r = subprocess.run([sys.executable, argv[1], "--workspace", ws] + [x.strip('"') for x in rest], cwd=SK, capture_output=True, timeout=300,
                           env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
        if r.returncode: bad.append((c, r.stderr[-200:]))
    T("every CLI command in SKILL.md runs as written from the skill folder (%d commands, bundled files only)" % len(cmds), cmds and not bad, bad)
    shutil.rmtree(ws, ignore_errors=True)
    req = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "c", "version": "1"}}}) + "\n"
    o = subprocess.run([sys.executable, os.path.join(SK, "scripts", "spindoctor_mcp.py")], input=req.encode(), capture_output=True, timeout=60).stdout.decode()
    T("optional MCP server (scripts/spindoctor_mcp.py) answers initialize", '"serverInfo"' in o and '"tools"' in o, o[:200])
    o = subprocess.run(["node", os.path.join(HERE, "plugin_smoke.mjs")], capture_output=True, text=True, timeout=300).stdout
    try: j = json.loads(o.strip().splitlines()[-1])
    except (ValueError, IndexError): j = {"ok": False, "checks": o[-300:]}
    T("tests/plugin_smoke.mjs: module shape, JSON-Schema route (6 tools, nullable optionals, qc-001, function table), zod route", j.get("ok"), j.get("checks"))


def free_port():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p


class Host:
    def __init__(self, kilo):
        self.kilo = kilo; self.tmp = tempfile.mkdtemp(prefix="sdq_kilo_"); self.home = os.path.join(self.tmp, "home")
        self.cfg = os.path.join(self.home, ".config"); self.port = free_port(); self.n = 0
        self.env = dict(os.environ, HOME=self.home, USERPROFILE=self.home, XDG_CONFIG_HOME=self.cfg, XDG_CACHE_HOME=os.path.join(self.home, ".cache"),
                        XDG_DATA_HOME=os.path.join(self.home, ".local", "share"), XDG_STATE_HOME=os.path.join(self.home, ".local", "state"), NO_COLOR="1")
        for k in ("KILO_PURE", "SPINDOCTOR_WORKSPACE", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "KILO_API_KEY", "OPENROUTER_API_KEY"): self.env.pop(k, None)
        os.makedirs(os.path.join(self.cfg, "kilo"))
        json.dump({"$schema": "https://app.kilo.ai/config.json", "autoupdate": False, "model": "stub/stub",
                   "provider": {"stub": {"npm": "@ai-sdk/openai-compatible", "name": "Local stub",
                                         "options": {"baseURL": "http://127.0.0.1:%d/v1" % self.port, "apiKey": "local-stub"},
                                         "models": {"stub": {"name": "stub", "tool_call": True}}}}},
                  open(os.path.join(self.cfg, "kilo", "kilo.json"), "w"), indent=1)

    def project(self, name, plugin=None):
        d = os.path.join(self.tmp, name); os.makedirs(d); subprocess.run(["git", "init", "-q"], cwd=d)
        if plugin: json.dump({"$schema": "https://app.kilo.ai/config.json", "plugin": [plugin]}, open(os.path.join(d, "kilo.json"), "w"))
        return d

    def run(self, cwd, script, prompt="go"):
        self.n += 1; log = os.path.join(self.tmp, "stub%d.jsonl" % self.n); sp = os.path.join(self.tmp, "script%d.json" % self.n)
        json.dump(script, open(sp, "w"))
        stub = subprocess.Popen([sys.executable, os.path.join(HERE, "stub_llm.py"), str(self.port), log, sp], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(0.8)
        try:
            p = subprocess.run([self.kilo, "run", prompt, "--format", "json"], cwd=cwd, env=dict(self.env, PWD=cwd),  # Kilo reads $PWD
                               capture_output=True, text=True, timeout=900)
        finally:
            stub.terminate(); stub.wait()
        recs = [json.loads(l) for l in open(log)] if os.path.exists(log) else []
        agent = [r for r in recs if r["tools"]]
        return p.returncode, p.stdout + p.stderr, (agent[-1]["tool_results"] if agent else []), (set(agent[0]["tools"]) if agent else set()), (agent[0] if agent else {})


def sysprompt(rec):
    return json.dumps(rec.get("system") or "")


def real(kilo, source):
    h = Host(kilo)
    ver = subprocess.run([kilo, "--version"], env=h.env, capture_output=True, text=True).stdout.strip().splitlines()[-1]
    T("Kilo Code CLI runs: kilo " + ver, re.match(r"\d+\.\d+\.\d+", ver), ver)
    # --- route A: project .kilo/
    proj = h.project("proj-a")
    o = subprocess.run([sys.executable, INSTALL, proj], capture_output=True, text=True).stdout
    T("tools/install_kilo.py PROJECT copies plugin + skill into PROJECT/.kilo/", os.path.isfile(os.path.join(proj, ".kilo", "plugin", "spindoctor-qwerty.js"))
      and os.path.isfile(os.path.join(proj, ".kilo", "skills", "spindoctor-qwerty", "SKILL.md")), o)
    shutil.copy(os.path.join(SK, "examples", "theory", "hadamard_theory.txt"), os.path.join(proj, "my_theory.txt"))
    ws = os.path.join(h.home, "spindoctor-workspace")
    script = [{"tool": "spindoctor_functions", "args": {}},
              {"tool": "spindoctor_run_script", "args": {"script": BELL}},
              {"tool": "spindoctor_run_preset", "args": {"preset_id": "qc-001"}},
              {"tool": "spindoctor_test_theory", "args": {"action": "extract", "source": "file", "path": "my_theory.txt"}},
              {"tool": "spindoctor_test_theory", "args": {"action": "run", "source": "chat",
               "text": "From our chat: H then CX makes a Bell state, so 00 and 11 each appear about half the time.",
               "excerpts": ["User: does H then CNOT give 50/50 on 00 and 11?", "Assistant: yes, that is a Bell state."],
               "hypothesis": "H(0) then CX(0,1) gives P(00) = P(11) = 0.5", "prediction": "P(11) = 0.5 +/- 0.05 over 4000 shots",
               "script": "q.circuit new bt 2\nq.circuit add h 0\nq.circuit add cx 0 1\nq.circuit run shots 4000 basis z",
               "checks": [{"kind": "probability", "outcome": "11", "expected": 0.5, "tolerance": 0.05}]}},
              {"tool": "skill", "args": {"name": "spindoctor-qwerty"}},
              {"tool": "bash", "args": {"command": "cd \"$SKILLDIR\" && python3 scripts/spindoctor_cli.py preset qc-002", "description": "Run SpinDoctor preset qc-002"}},
              {"text": "done"}]
    code, out, res, offered, rec = h.run(proj, script, "show the SpinDoctor functions and test the Bell theory we discussed")
    T("project route: kilo run exits 0 and the session offers the 6 tools + skill + bash", code == 0 and set(TOOLS) <= offered and {"skill", "bash"} <= offered, (code, sorted(offered), out[-300:]))
    sch = (rec.get("schemas") or {}).get("spindoctor_run_script") or {}
    T("project route uses the zod schemas (Kilo installed @kilocode/plugin in .kilo/): run_script requires only `script`",
      sch.get("required") == ["script"] and os.path.isdir(os.path.join(proj, ".kilo", "node_modules", "@kilocode", "plugin")), sch)
    T("skill listed in the system prompt (<available_skills> spindoctor-qwerty)", "<name>spindoctor-qwerty</name>" in sysprompt(rec))
    T("spindoctor_functions: the Markdown function table verbatim", len(res) > 0 and "| Function | What it does | Command to type |" in res[0], res[:1])
    T("spindoctor_run_script: Bell circuit ok", len(res) > 1 and OK(res[1]) and "bell" in res[1], (res[1:2] or [""])[0][:300])
    T("spindoctor_run_preset qc-001 ok", len(res) > 2 and OK(res[2]) and "qc-001" in res[2], (res[2:3] or [""])[0][:300])
    T("relative path `my_theory.txt` resolves against the session's project folder (theory extract ok)", len(res) > 3 and OK(res[3]) and "my_theory.txt" in res[3], (res[3:4] or [""])[0][:300])
    pdf = re.findall(r'"([^"]+theory[^"]*\.pdf)"', res[4]) if len(res) > 4 else []
    T("spindoctor_test_theory from the chat: supported, 2 excerpts, valid PDF under ~/spindoctor-workspace",
      len(res) > 4 and '"verdict": "supported"' in res[4] and '"excerptsRecorded": 2' in res[4] and pdf and os.path.isfile(pdf[0])
      and open(pdf[0], "rb").read(5) == b"%PDF-" and pdf[0].startswith(ws), (res[4:5] or [""])[0][:300])
    skdir = os.path.join(proj, ".kilo", "skills", "spindoctor-qwerty")
    T("skill tool loads SKILL.md with Kilo's base directory = the installed skill folder", len(res) > 5 and "Base directory for this skill: " + skdir in res[5], (res[5:6] or [""])[0][-300:])
    T("bash fallback: the CLI from the skill's base directory runs preset qc-002", len(res) > 6 and "qc-002" in res[6] and OK(res[6]), (res[6:7] or [""])[0][:300])
    # --- route B: global ~/.config/kilo/
    o = subprocess.run([sys.executable, INSTALL, "--global"], env=h.env, capture_output=True, text=True).stdout
    gdir = os.path.join(h.cfg, "kilo")
    T("tools/install_kilo.py --global copies plugin + skill into $XDG_CONFIG_HOME/kilo/", os.path.isfile(os.path.join(gdir, "plugin", "spindoctor-qwerty.js")), o)
    projb = h.project("proj-b")
    code, out, res, offered, rec = h.run(projb, [{"tool": "spindoctor_list_presets", "args": {"filter": "ghz"}}, {"text": "done"}], "list GHZ presets")
    T("global route: a fresh project gets the 6 tools and the skill; list_presets ghz ok", code == 0 and set(TOOLS) <= offered and "<name>spindoctor-qwerty</name>" in sysprompt(rec)
      and res and OK(res[0]) and "ghz" in res[0].lower(), (sorted(offered), (res or [""])[0][:200]))
    o = subprocess.run([sys.executable, INSTALL, "--uninstall", "--global"], env=h.env, capture_output=True, text=True).stdout
    code, out, res, offered, rec = h.run(projb, [{"text": "ok"}], "hello")
    T("--uninstall --global: the next session has no SpinDoctor tools or skill", code == 0 and not (set(TOOLS) & offered) and "spindoctor-qwerty" not in sysprompt(rec), sorted(offered))
    # --- route C: git plugin spec
    if source:
        spec = "git:" + source
    else:
        rep = os.path.join(h.tmp, "repo"); shutil.copytree(ROOT, rep, ignore=shutil.ignore_patterns(".git", "__pycache__", "node_modules"))
        for c in (["init", "-q", "-b", "main"], ["add", "-A"], ["-c", "user.name=check", "-c", "user.email=check@localhost", "commit", "-qm", "check"]):
            subprocess.run(["git"] + c, cwd=rep, check=True, capture_output=True)
        spec = "git:" + rep
    projc = h.project("proj-c", spec)
    code, out, res, offered, rec = h.run(projc, [{"tool": "spindoctor_run_script", "args": {"script": BELL, "workspace": None}},
                                                {"tool": "spindoctor_run_preset", "args": {"preset_id": "qc-003", "overrides": None, "workspace": None}}, {"text": "done"}], "run a Bell circuit")
    sch = (rec.get("schemas") or {}).get("spindoctor_run_script") or {}
    T("git route (`plugin: [\"%s\"]`): Kilo clones it and registers the 6 tools" % spec.split("/")[-1], code == 0 and set(TOOLS) <= offered, (sorted(offered), out[-300:]))
    T("git route uses the JSON-Schema definitions (no dependencies installed): workspace is nullable", "null" in json.dumps(sch.get("properties", {}).get("workspace", {})), sch)
    T("git route: Bell circuit and qc-003 ok with null optionals", len(res) > 1 and OK(res[0]) and OK(res[1]), [x[:150] for x in res])
    T("git route: the skill is not loaded (documented; install_kilo.py adds it)", "<name>spindoctor-qwerty</name>" not in sysprompt(rec))
    # --- shared end-to-end suite
    e2e = os.path.join(HERE, "e2e_results.json")
    p = subprocess.run([sys.executable, os.path.join(HERE, "e2e_mcp.py"), "--server", sys.executable, os.path.join(SK, "scripts", "spindoctor_mcp.py"),
                        "--examples", os.path.join(SK, "examples", "theory"), "--out", e2e], env=h.env, capture_output=True, text=True, timeout=3600, cwd=h.tmp)
    last = [l for l in p.stdout.splitlines() if l.strip()][-1:] or [""]
    T("shared end-to-end suite through the bundled MCP server: " + last[0][:60], p.returncode == 0, p.stdout[-500:])
    return "kilo " + ver


def main():
    a = sys.argv[1:]; opt = dict(zip(a[::2], a[1::2]))
    static(); ver = None
    if opt.get("--kilo"): ver = real(opt["--kilo"], opt.get("--source"))
    out = opt.get("--out", os.path.join(HERE, "host_check.json"))
    json.dump({"python": sys.version.split()[0], "host": ver, "checks": R}, open(out, "w"), indent=1)
    n = sum(r["pass"] for r in R); print("%d/%d passed" % (n, len(R))); return 0 if n == len(R) else 1


if __name__ == "__main__":
    sys.exit(main())
