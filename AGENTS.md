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
- Delegate to subagents only when the user explicitly requests delegation.

## Validation

- Run playable client checks at 1920×1080 by default. When a Full HD run
  is unavailable, use at least 1280×720 and record the actual render size.
- Use targeted checks appropriate to changes. For parsers, keep small reproducible
  examples and verify real inputs, boundaries and malformed data.
- Keep legacy build reproduction separate from compiler migration and renderer work.
- Update the audit and next steps when a blocking condition is resolved.
