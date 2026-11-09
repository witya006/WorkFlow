# Память проекта

Обновлено 2026-11-10. **131 PARTIAL M6**.
Текущий gate: inventory/client455-light-direction-checkpoint.json.
Проверка: scripts/Invoke-Python.ps1 scripts/checkpoint_client455_light_direction.py.
Доказательства: research/client455-light-direction.md.
Runtime130 исторический, статические доказательства и изображения сохранены.
Предыдущая полная память: research/project-memory-before131.md.
Предыдущий goal turn130: progress, commit64636cd. Текущий131: progress.

## Цель и правила

CLIENT ONLY: поддерживаемые исходники и свой RF_Online.bin с полным поведением455.
M9 УЖЕ определён: финальная приёмка без модернизации графики. Не повторять вопрос
из старого Goal. M0–M4 diagnostic/selectedM5 выполнены; M6/M6F/M7/M9 OPEN, M8 не нужен.
Build/Create1/selected component не закрывают docs/client-acceptance.md.
Server только читать как reference; не менять, не собирать, не восстанавливать.
Originals immutable, inputEXE never execute, copies under work/, Git local/no push.
Subagents только по явному запросу. Python scripts/Invoke-Python.ps1 file.py, не -c/-m.
VS2026 MSVC x86. Native/GPU jobs sequential; timeout не restart, дождаться terminal
того же handle. Перед runtime edit exact engine/PE/MAP/rsp/reports backup.
Ignored != backup. Не повторять159k/unchanged bulk suites без нового риска.
Updates коротко RU <=60s. rg --files перед неизвестными именами, не shell path globs.

## Подтверждено131

Primary SHA b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b.
Secondary46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.
x86/base400000.10fullasm/411instructions/11ranges equalboth455:
5primary315 +5CRT context96, полные CFG и все positive block starts.
5primary pcode полны; CRT start_3 Hex-Rays failed, full CRT pcode НЕ заявлен.
Raw/session artifacts/client455-progress/light-direction131-*.json.
Owned session1ff3df20 saved/closed/list0. Live native jobs отсутствуют.
MCP <=100asm/page, counts/unique/done AND all positiveCFG starts/tails; не alias
firstpage.asm.lines и aggregate. Save JSON chunks <=20k via Node, не печатать весь raw.

VA8BFBC0 affine inverse и8C0980 transform уже были восстановлены в x87 library.
130 ошибочно назвал Vector3fTransform legacy: actual source уже использовал точный
wrapper.131 повторно использует этот backend, заменяет D3DX inverse и отдельный
геометрический normalizer в light branch. Новая обычная цепочка:
prepareEntityShader455 -> RF455_BuildLightDirection -> inverse -> zero translation
-> transform -> RF455_NormalizeLightVector -> RF455_LightSqrt.
Main normalizer VA51D5D0/136bytes повторён инструкциями кроме CALL sqrt backend.
Нормализатор геометрии130 НЕ менялся: у него другой порядок операций.
Inverse guards0.001; caller игнорирует failure и потребляет unspecified stack bytes.
НЕ добавлять fallback. Direct guard tests не доказывают output такого caller.

Sqrt wrappers41DB70/41DB90 -> CRT874514/start87451D. __load_CW888DD5:
temporaryCW=(callerCW&0x300)|0x7f. FSQRT nearest, callerPC сохранён; затем restore
callerCW и float store с callerRC. Перенесена выбранная finite nonnegative policy.
CRT matherr/errno/precision-error callbacks, unmasked exceptions, full NaN/Inf/
status flags всё ещё OPEN; не заявлять полное sqrt/CRT equivalence.
Normalizer sum x*x+y*y+z*z -> float square -> float sqrt -> double spill -> divs.
Zero normal остаётся x87 indefinite, без нового направления по умолчанию.

240CPU:96normal+96affine+48guards в12PC/RC modes; independent Fraction oracle
rounds each operation and sqrt via integer midpoint. Selected outputs bitexact.
72actual LitGrass draws/6world transforms/12FPmodes: shader19.xyz bitexact.
Main/CPU PE: inverse485/transform132/normalizer136 byteidentity except epsilon/
verified sqrt CALL. CPU BuildLightDirection inlined; ordinary PE retains owner.
New full-object GPU lab work/m9/27c783ee/light-direction-001.
5frames +72draws/stock300byte shader/36stride/8materialcases/3bumptimes/5328
geometry normals exact. CPU source is client455_light_direction_probe.cpp.
One compile failure: wrong test helper control125; correct setCW125, fixed.
One audit failure demanded noninlined CPU owner; now require only in ordinary PE.

## Текущая сборка и регрессии

Engine9f33478968c77b1a81acd031c50acd2175e7e37d129a067d16257e810175011e.
67objects/21derived,1payload(renderentity) changed/66byteequal130; no timestamps-only.
Shared camera/vertex/particle/core/level headers unchanged;182client/20kernel objects
preserved, no redundant full rebuild. Short ANI/BBX consumers rerun PASS.
PEd1738f4e7516f33867c9fa7d3dc3219e684843dc49fec456e01eaa96783496b5.
2255872bytes/x86/base400000/entry16C9B0/WinMainB98B0/afterCreateB9A24/unresolved0.
No CharacterMR/no FORCE. Exact own-entry/providers/sound1/window/device/
existingCreate1/contracts PASS. Known handled first-chance40080201/E06D7363/
406D1388 remain; full bootstrap/game loop not accepted.

Fresh world76queue/16clock/6oldwarnings,material60profiles/36cases/1missing,
fade90+27/0warnings,lighting867colors/3aggregates/27Mie/29BSP/2warnings,
weather90scripts/5aggregates/1missing PASS. All30new raw+PNG framecontents byteequal
reviewed130. Explicit review reuse, no new visual inspection. New CLI
reuse_client455_visual_review.py light-direction --snapshot before131
--reference-prefix lighting-consumers. Same-prefix regressions use before131.
Never reuse if pixels differ. Exact130 before131 snapshots include reports,
engine/PE/MAP/rsp/sharedcamera+vertex headers and research memory/next backups.
Prior130 gate is pinned historical. New feature CLIENT455-LIGHT-DIRECTION-131 current.

## Следующие участки

132: actual game writers/selection of CEntity flag40,typed owners and flags across
real creation/load/callers; don't infer gameplay from lab flags. Then material
runtime526/layer54/extra8/capacity vs source332/layer46/max4 and shader lifecycle.
Serialized46 -> runtime54 confirmed at90B1C0; do not cast source to526.
Broader slots plausible7, no constructor proof yet. LitGrass3-register overreads:
shader reads19.xyz/21/22; source deterministic unused lanes, later consumer proof OPEN.
Shader caps/failure/reset/OOM, exact CRT, lensflare/localfog/indirect params,
INS/Planet/world visibility/camera/alpha/textures/UI/stages/auth/protocol/Character/
gameplay/full client-acceptance remain OPEN. NeutralB upward camera/thin strips
remain an explicit unknown fidelity gap; unchanged frames do not close it.

Keep128 lighting lag: previousorbit/currentfar -> Sun position, then newSun/Mie;
tint uses OLDfog, then newfog. Fogflag2 endpoints else289grid17x17; no zero-divisor
fallback. NegativeZzero=-0; exact19h Mie discontinuity preserved. R3X4day/8night,
absent endpoints retain previous; FOG_COLOR current/main5/5000 not day distances.
129 tags uppercase90A5ED forFOG/ENV,lower90ACEC forweather/scene flags.
Packedweather1157D3C BSS0 persistsInitCore/R3X, fullDWORD OR spill, no byte clamp.
Missing trade_bel.r3e never substitute. Lab temporaryCLevel must outlive active map:
its destructor releases global resources. D3D observers patch originalFULLvtable
57/82/83, restore around forward/Get; never clone119 entries(private driver slots).
Goal active; M6/M6F/M7/M9 OPEN. Don't pause/block/complete for partial progress.
