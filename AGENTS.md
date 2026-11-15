# RF Online workspace instructions

## Scope and evidence

- CLIENT ONLY: reconstruct the RF Online client from legacy client/R3Engine code
  toward client 455. Work on R3Engine and asset tools only as client dependencies.
- Delivery target: maintainable source that builds RF_Online.bin with the full
  functionality and behavior of the pinned 455 client. Track all known gaps;
  compilation, launching or a partial vertical slice is not project completion.
- Server source files may be read as reference material for client contracts.
  Do not modify, build or restore those files, including working copies.
- Server source claims must be verified against the 455 client before treating
  them as its behavior. Follow docs/client-acceptance.md for completeness evidence.
- Do not build, restore, implement or plan AccountServer, LoginServer, ControlServer,
  ZoneServer, server databases or GoMMO server logic. Their absence is not a client blocker.
- First build target is client dependency R3Engine - Win32 RTMovie Release;
  final executable target is RF_Online. Prior LoginServer build decision is revoked.
- Primary build environment is installed VS 2026 Professional / modern MSVC x86.
  Port settings from the legacy DSP into a modern project; VC6 is fallback only,
  not a prerequisite. Keep renderer modernization separate from this port.

- Main working root: E:\RFOnlineTrash\Source\WorkFlow.
- Read README.md, docs/environment-audit.md and docs/next-steps.md before new work.
- Read docs/project-memory.md for current decisions; use docs/roadmap.md when planning.
- After a completed milestone, update project-memory.md and next-steps.md; keep
  detailed evidence in inventory/ or research/, not in conversational memory alone.
- Treat directories in config/paths.json as reference inputs. Work on copies under
  work/ unless the user explicitly requests changes to the original installation.
- Do not recode or normalize legacy source files during inventory.
- Record binary SHA-256, architecture and RVA for binary-analysis findings.
- Separate confirmed facts, hypotheses and unknowns. A file name, README claim,
  matching string or decompiler output is not proof of version or equivalence.
- Distinguish client behavior, reference server behavior and GoMMO server behavior.

## Workflow

- Localization work and acceptance cover Taiwan (`zh-tw`) and Russian
  (`ru-ru`). Preserve existing code and evidence for other locales as history.

- Latest user direction 14.11.2026: begin resource loading/caching, then complete
  one of the existing 12 domains at a time. Files/data is first in work order;
  preserve domain identities and previous evidence.
  Do not build RF_Online.bin until the active domain's implementation checklist
  is complete. Standalone non-graphical component tests are allowed; root owns
  their builds/runs. Fix test failures before the next domain. User owns gameplay
  and visual acceptance. Implementation-complete, component-tested and user-accepted
  are distinct; never claim 100% legacy equivalence from static analysis alone.
  New evidence reopens affected requirements and prior implementation as needed.
- Two roles per bounded contract: root reverses pinned 455 and reviews integration;
  one implementation agent owns explicit source files. Send versioned contracts
  with evidence, edge cases and unknowns; corrections update contract and code.
  Two passes mean understanding and implementation/review per feature, not two
  complete passes over the binary or a guarantee of full recovery in two passes.
- Preserve existing source/history. Cache immutable shared resources with bounded
  lifetime and memory budget; mutable actor state remains per instance. Do not
  assume repeated file reads imply repeated physical I/O. x86 LAA (up to 4 GiB on
  x64 Windows) and x64 migration (>4 GiB ordinary address space) are separate tasks.
  Preserve wire/file layouts with fixed-width types; do not widen serialized fields.

- Current process: docs/engineering-workflow.md; queue: config/task-board.json.
  Continue existing M6. Do not treat historical checkpoint logs as a task queue.
  Latest priority is functional contracts and targeted internal improvements;
  previous lobby visual work is preserved, not a gate on gameplay restoration.
- Visual target is Clair Obscur: Expedition 33 while preserving RF identity.
  Preserve the visual result; runtime diagnostics now come from user runs.
  No UE5 port or wholesale rewrite.
- One active package, one build/game-session owner. A package specifies outcome,
  changed files, acceptance, focused check and next action. After 30 minutes with
  no new fact or two failed attempts of one approach, revise that approach.
- Run scripts/workspace.py status through Invoke-Python before/after a package.
  Limits are in config/workspace-policy.json. Reuse immutable assets and one current
  runtime/one rollback. No unbounded hash/run directories or full-client copy per test.
- Do not delete unique source/evidence or bypass a storage failure to continue.
  Work under work/ is ignored, not disposable by default. Historical evidence from
  cleanup is indexed in artifacts/workspace-cleanup-20261113/unique-evidence.zip.
- Keep scripts, documentation and small manifests in this local Git repository.
- Keep raw assets, working source copies, IDA databases and large traces in the
  ignored work/ or artifacts/ directories. Ignoring a file is not backing it up.
- Do not commit credentials, session tokens, account data, database dumps or logs.
- Use scripts/Invoke-Python.ps1 for the verified audit interpreter.
- GoMMO MCP discovery is reproducible through scripts/probe_gommo.py. Check actual
  returned schemas before any new tool call. Audit uses initialize, tools/list and
  studio_status only. Audit authorization does not imply Install or publishing.
- IDA MCP is installed and registered as ida_mcp using the local venv and idalib
  supervisor. See docs/ida-mcp.md. Verify it using probe_ida_mcp.py --configured.
  Open copies under work/ with idb_open, pass its database session ID to every
  analysis call, and close owned sessions with idb_close. Never execute input EXEs.
- Do not assume a current native MCP tool registration from a config file alone.
- Do not add remote repositories, publish assets or push commits unless requested.
- User authorized subagents on 13.11.2026 when they accelerate the work without
  harming it. Delegate bounded independent tasks with explicit file ownership;
  keep integration, builds and live game sessions under one owner.

## Validation

- Latest user direction 15.11.2026: root may launch and play the local beta under
  the debugger to verify fixes autonomously. Use 1920×1080 (minimum 1280×720)
  and the dedicated test account. Verify one kill, one NPC sale, one NPC
  purchase and one teleport. User acceptance remains a separate milestone.
- Review formats, boundaries and ownership; use focused standalone CPU tests for
  changed components. Full client builds are gated on active-domain implementation
  completeness. Existing unrelated checks are not rerun automatically.
- Keep legacy build reproduction separate from compiler migration and renderer work.
- Update the audit and next steps when a blocking condition is resolved.
