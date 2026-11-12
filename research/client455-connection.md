# M6 / Initial connection052

## Закрытие и повторное подключение

13.11.2026. В `71dd9600…` события Winsock обрабатываются независимо.
Событие `FD_CLOSE` завершает подключение при штатном закрытии и при
сбросе TCP. Состояние события очищает `WSAEnumNetworkEvents` вместе
с чтением уведомлений. Рабочий поток больше не очищает его повторно
после вызова. [WSAEventSelect](https://learn.microsoft.com/en-us/windows/win32/api/winsock2/nf-winsock2-wsaeventselect) ·
[WSAEnumNetworkEvents](https://learn.microsoft.com/en-us/windows/win32/api/winsock2/nf-winsock2-wsaenumnetworkevents).

При закрытии снимается отложенное подтверждение из очереди. Обработчик
сбрасывает состояние сервера, назначенного этому процессу. Для основного
подключения сохраняется отмена ожидающих переходов и движения. Сообщение
об обрыве отображается для опубликованного подключения при готовом
интерфейсе. Ошибка до готовности интерфейса остаётся в маршруте запуска.

На локальном TCP-стенде собственный клиент принял штатное закрытие до
подтверждения подключения, аварийный сброс после подтверждения и штатное
закрытие после повторного подключения. Событие закрытия от неназначенного
процесса сохранило активное игровое соединение. Полный игровой выход по
диалогу, последние сообщения на границе закрытия и повторный вход в мир
остаются открытыми. [Манифест](../inventory/client455-disconnect-native.json).

## Первоначальный вход

2026-11-06. CLIENT ONLY. M6/M6F/M7/M9 remain OPEN.

The normal WinMain now performs the real initial TCP connection/wait before
InitR3Engine. A zero raw transport result is followed by the target events-only
pump and the actual connected flag. The Korean CCR fixture reaches engine,
Miles, D3D and the existing CMainApp::Create through a genuine TCP connection.
The fixture supplies no RF messages, authentication result or game protocol.

## Reference contracts

Current455 SHA-256
`b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`;
backup `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.
Both x86/base0x400000. Fifteen selected function ranges and11 country vtables
match in both pins. These input executables were only read.

| Area | RVA | Confirmed behavior |
|---|---|---|
| Initial connection | 0x3d1150 | Endpoint1/process0; global ./DataTable/ClientSystem.ini Network/ConnectTime, default90 seconds, DWORD multiplication by1000 |
| Country bypass | 0x42c7b0 | All11 country vslot284 entries select this false-returning function |
| Wait event pump | 0x4aa100→0x4ae0f0→0x4ad3a0 | Events/receipt only; no packet dispatch or UserLoop at this stage |
| Wait ordering | 0x3d129e–0x3d1348 | Capture now, pump events, test connected, test unsigned elapsed>budget, then Sleep4 |
| Event receipt | 0x4ad3a0 | At most102 accept/102 close/102 ready entries per call, counting failed accepts too |
| Client socket acceptance | 0x4b0420 / 0x4ac900 | Publish socket flags/time/serial, reset both buffers; defer application callback until elapsed>1000 |
| Connected query | 0x139b90 | Reads actual connected state; does not infer it from raw result0 |

Nonzero initial Connect returns immediately through NDLanguage6BE. Timeout reads
WSAGetLastError, formats NDLanguageBFA, hides the app window, shows MessageBoxA
and returnsfalse. The wait budget begins after the synchronous Connect call;
blocking Winsock time and error-dialog setup are outside that budget. Capturing
now before the pump and checking connected before elapsed are observable at
the boundary. Equality does not time out; a newly connected event wins over an
already exceeded budget. DWORD tick and multiplication wrap are preserved.

The source _Receipt previously allowed a callback at exactly1000ms and drained
queues without the target budget. It now uses strict>1000 and the102-entry
limit. Existing OnLoop still performs its broader legacy processing; a separate
PumpEvents455 is used only for the pre-engine wait.

## Russian/European profile limit

Confirmed reference facts: the Russian argv loader at RVA0x436cb0 writes
endpoint0; the initial connect chooses endpoint1; the getters read their raw
arrays and Init zeroes them. In the current reconstructed source the argv
profile leaves endpoint1 unset, and the real connection method times out.
This is recorded as an open country-bootstrap gap, not fixed by redirecting
endpoint indices.

It is **not** proof that the complete reference client always fails in this
profile: the remaining455 handler constructors/country providers may have
side effects that are not restored yet. Their complete behavior is unknown.
The exact own Russian WinMain trace now stops at the decoded call before
Connect. It proves launcher/language/FG/network creation/instance processing,
and does not claim sound or successful connection. A separate real-method
native probe exercises and records the current failure/error dialog.

## Source and verification

- `client455_connection.{h,cpp}`: shared wait ordering/boundaries and DWORD
  timeout parsing. Production callbacks use timeGetTime, actual PumpEvents455,
  IsConnectedToServer(1) and Sleep(4).
- `client455_connection_bridge.inc`: actual noinline CMainApp::ConnectNetwork455,
  real ConnectToServer455(1,0), localized error handling and diagnostic outcome.
  Normal WinMain checks its result before calling InitR3Engine.
- `client455_network_receipt.inc`: bounded receipt queues and delayed callback;
  wired to the normal CNetProcess. Packet decoding remains outside this wait.
- Full-object native helper tests equality/overflow/order with controlled clocks,
  the real profile API and an actual103-entry receipt queue. It calls the real
  CMainApp connection method for positive TCP, timeout and the argv-profile gap.
- Positive test verifies getpeername on the actual client socket and the owned
  listening port, followed by the real already-connected raw-error path.
  The negative tests preserve the confirmed raw0-after-close quirk and still
  returnfalse because connected remainsfalse. All three exit naturally with0.
- Error dialogs are real MessageBoxA calls. A test-only hook on the helper's own
  thread captures their text and closes them with a deferred timer. Text matches
  the actual NDLanguage format/error. No production API, branch or return value
  is replaced. The deferred close allows normal dialog initialization.
- `client455_tcp_fixture.py` owns a temporary loopback TCP socket and thread,
  sends zero bytes and implements no RF protocol. Every run records connection
  count and closure. Ports are generated and encoded into synthetic owned CCR
  data. Actual game/server sources and installations are not modified.

The own debugger still controls only its newly launched owned PE. A labelled
checkpoint file permits a precise pre-connect stop for argv profiles; it is
validated before process creation. Breakpoints are restored and no EAX or
conditional branch is overridden. Device probes obtain a fresh TCP fixture
rather than reusing an expired port from an earlier run.

Final own PE SHA-256
`0733cce1ed6e77e2d70646ddc281129629d029421888cda6adff2f01a433a53a`,
x86/base0x400000/entryRVA0x14a3f0,2,012,160bytes.182 normal client objects,
20 canonical kernels,21 facade units; link0 unresolved. Engine unchanged.
Own decoded points: beforeConnect0xb4435→method0xb38e0, afterConnect0xb443a,
afterSound0xb4458, afterD3D0xb4468; existingCreate returned1 at0xb447a after
CALL0xb4475→0xb3ac0. Its controlled debugger stop is not a natural full-game
exit or complete455Create acceptance. The connected debug event precedes the
sound checkpoint; decoded calls also prove Connect is before InitR3Engine.

Evidence: `inventory/client455-connection-{reference,native,checkpoint}.json`,
own-entry/startup/UI reports, normal build/link. Raw IDA output is ignored under
`artifacts/client455-connection/`. Owned sessionbed1c136 closed/save=true.

## Remaining work / next053

Recover gate crypto request/reply consumers569CD0/569D30 and their downstream
packet state, remaining wire layouts and all35 handlers. Keep the current
Russian/European endpoint issue open while restoring missing constructors and
country providers. Then complete actual login/UI/game tables and gameplay.

Full transport/queued route/filters/internal security/threads/Close/error
ownership, FT/IME/layout/ILevel/world and full shutdown remain mandatory.
Bounded error formatting and the selected clock/socket tests do not certify
all unsafe/OOM/concurrency/old-CRT/window-ownership domains. TCP connection
success alone is not game authentication or M9 acceptance.
