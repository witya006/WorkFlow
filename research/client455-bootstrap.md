# M6 / Bootstrap050: FG, single instance and client network state

2026-11-06. CLIENT ONLY. M6/M6F/M7/M9 remain OPEN.

The normal client now reads FG settings, creates its actual network manager and
checks the country-specific instance policy before engine initialization. The
old network creation inside CMainApp::Create is removed, so initialization runs
once. This is a partial restoration of the target bootstrap sequence: the
pre-engine connection/wait phase and the full455 network implementation remain.

## Reference and confirmed contracts

Current RF_Online.bin SHA-256
`b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`;
backup `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.
Both x86, image base0x400000. All28 selected function ranges and11 country
vtable ranges match between these pins. These binaries were only read.

| Area | Reference RVA | Confirmed behavior |
|---|---|---|
| WinMain / FG setter | 0x3d04e0 / 0x3d0cd0 | root/FG_CB.ini, SETTING/USEFG default0, GetPrivateProfileString nSize4, atol, store the raw integer |
| Empty bootstrap call | 0x3d2b90 | No body between FG and network initialization |
| Instance filename/process/mutex | 0x3cf720 / 0x3cf7c0 / 0x3cf8a0 | Uppercase filename+extension must be13-byte RF_ONLINE.BIN; process count>1 rejected; existing Global mutex rejected |
| Network creation entry | 0x3d10a0 | Calls the actual network member's virtual Create before engine; failure logged without a new WinMain gate |
| Network Create / Destroy | 0x161000 / 0x162160 | 35 message-handler objects, two configured processes; distinct from the old client's12 handlers and one process |
| Connect state / Accept | 0x162350 / 0x1627e0 | Six active-endpoint bytes, four connected DWORDs; raw return0 versus nonzero; callback process0 on direct branch |
| Transport / standard TCP | 0x4a9ee0 / 0x4b0480 | AF_INET/htons, standard/queued routing; standard error read after closesocket, event-selection failure -3 |

Instance bypass follows country vslots252/240/292/256: Russia/China/Europe/Taiwan
(nation7/2/3/8). Japan's title selector does not bypass this check. The target
accepts CreateMutexA failure if earlier checks pass; an existing handle produces
failure after ReleaseMutex. It retains the handle until process exit. The own
implementation retains handles until its CRT cleanup. Error texts use NDLanguage
BF5/BF6, BF7/BF8, BF9/BF8; full target error logging/window ownership is not certified.

USEFG's semantic purpose beyond the stored integer has not been established.
This work neither invents a provider nor assumes the flag authenticates anything.

## Source changes

- `scripts/native/client455_bootstrap.{h,cpp}`: real Windows profile, filename,
  process and mutex operations. `client455_bootstrap_bridge.inc`: actual member Create.
- `client455_network_state.{h,cpp}`: source-owned six-process/four-endpoint connect
  state and raw result handling. Existing connected active endpoint returns-1;
  nonzero transport clears the requested endpoint's connected flag and preserves
  its previous active endpoint. A zero return publishes the requested endpoint.
- `client455_network_bridge.inc`: real normal CNetworkMgr adapter; it publishes
  the new active state before invoking its actual virtual callback. Endpoint2 or
  logout takes the target direct branch; the callback is still process0 even if
  another process was requested. Unsafe invalid-active callback domains are bounded.
- `client455_network_transport.inc`: forwards the actual CNetSocket::Connect
  integer. The old BOOL wrapper remains for existing callers. Its transport has
  not yet been replaced with the complete455 transport.
- `prepare_client455_normal.py`: integrates the above into the normal copied
  client, adds4endpoint storage/six active slots, moves Create before engine,
  preserves old wire structs as a documented gap. No reference/server edits.

## Important observed target quirk

The original455 instructions at VA8B0505 call closesocket **before** VA8B050B
calls WSAGetLastError. On this machine a real connection to an owned bound,
non-listening loopback port fails with10061 before close, then returns0 after
close. The independent WinSock oracle and the actual normal transport both show
this result. It is recorded rather than silently fixed:0 alone does not prove
an established connection. The connected flag remains false. The subsequent
target wait/pump checks that flag; this phase is still required.

The negative test creates no listening service or server emulator. Separate
component callbacks exercise state transitions only. Actual normal logout-path
testing uses endpoint1, which sends no packet; no authentication result is forged.

## Verification

- Full-object own console probe uses the182 normal client objects/current libs.
  It reads a copied real Korean FG_CB.ini, tests nSize4 truncation/default/raw
  integer cases, all11 policies, filename cases, real mutex reuse and a second
  own RF_Online.bin process. Both processes exit naturally. A differently named
  copy proves WrongFilename. No other process is controlled.
- State kernel covers all six process indices, endpoint/error/already-connected
  and direct callback behavior. The real manager is created; real TCP behavior,
  invalid-process error10022 and the actual logout callback are verified.
- New full own PE SHA
  `3b93b0ebab349dd0b2d41d970918d4933176eb33431ec547cb7a61db1439d738`,
  x86/base0x400000/entryRVA0x149010,2004992bytes. Build182client objects,
  20canonical kernels,19facade units; link0 unresolved. Derived engine unchanged.
- Exact own WinMain traces: Korean and Russian language→FG→NetworkCreate→instance
  policy→engine/Miles. Korean accepts instance; Russian bypasses. Each trace
  has exactly one NetworkCreate. The full own existing CMainApp::Create returns1
  at ownRVA0xb3f88, after CALL0xb3f83→Create0xb35e0. Controlled debugger stop;
  this is not a natural full-game exit or a complete455Create acceptance.
- Existing model/animation/GPU, counters/clock/effects, Korean/Russian text,
  sprites, launcher and lifecycle regressions pass. Seventeen scoped checkpoints
  pass their local contracts and retain PARTIAL status for the complete client.

Evidence: `inventory/client455-bootstrap-{reference,native,checkpoint}.json`,
own startup/UI reports and normal build/link reports. Raw decompilation and
instructions remain ignored under `artifacts/client455-bootstrap/`; native labs
under `work/m9/`. IDA sessions d716d7fa and8102ad50 closed with save=true.

## Remaining work / next051

Recover455 transport creation/configuration, two configured processes/six-capacity
routing, buffers, framing/cipher, pump/Accept and gate crypto request569CD0. The
old sender still has13-byte ID/password wire fields versus455state50/32. Full
35-handler message dispatch, Close/error/ownership semantics and country-specific
client contracts remain open. Do not infer any server behavior from these sources.

Then implement the real pre-engine ConnectToServer wait/pump at RVA0x3d1150,
including timeout/error behavior, without substituting successful authentication.
Target video/BGM/managers/fullUI/game tables, FT/ANSI/IME/layout, ILevel/world,
game actions and full shutdown are still mandatory before M6F/M7/M9.
