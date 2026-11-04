# RF Online workspace instructions

## Scope and evidence

- Main working root: E:\RFOnlineTrash\Source\WorkFlow.
- Read README.md, docs/environment-audit.md and docs/next-steps.md before new work.
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

- Use targeted checks appropriate to changes. For parsers, keep small reproducible
  examples and verify real inputs, boundaries and malformed data.
- Keep legacy build reproduction separate from compiler migration and renderer work.
- Update the audit and next steps when a blocking condition is resolved.
