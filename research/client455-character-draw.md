# Основной Character draw455: source-маршрутизация

2026-11-05. M6 в работе. Основной92E5F0 теперь представлен source-кодом вместе
с обработчиком эффектов, очередью прозрачности, deferred batch, CPU и shadow
маршрутами. Это ещё не полный normal455 renderer и не финальная приёмка M9.

## Эталон и инструменты

PE x86/base0x400000, current SHA-256
`b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`;
backup `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.
13диапазонов и5constant ranges равны обоим pin. Хеши, размеры, значения и RVA:
inventory/client455-character-draw-reference.json. Owned IDA96236a02 закрыта/save.

| VA | RVA | Назначение |
|---|---|---|
| 91C450 | 51C450 | Material68: diffuse/ambient RGBA,остальное0 |
| 92E5F0 | 52E5F0 | Основной Character draw |
| 92D330 | 52D330 | Bump oscillator от timeGetTime |
| 92D3E0 | 52D3E0 | Environment/scroll/bump stage |
| 92D270 | 52D270 | Reset1024transparent entries |
| 92D6C0 | 52D6C0 | Depth от first palette × sortView,element14 |
| 92D6F0 | 52D6F0 | Вставка в связанную очередь |
| 91F300 | 51F300 | Заполнение packet2060 |
| 92D9D0 | 52D9D0 | Mesh batch capture по10,до200 |
| 930650 | 530650 | Flush fixed-function batch |
| 92DB60 | 52DB60 | CPU retained mesh |
| 930A40 | 530A40 | Прозрачный проход |
| 930120 | 530120 | Shadow проход |

Raw evidence в ignored artifacts/character-animation455/route-*.json. Для main
собраны все1582instructions страницами120, фактическая длина каждой страницы
проверена. В прежнем draw-main-insn.json всего10lines при reported count982 и
cursor.done: нельзя считать его полной выгрузкой. Новая полная выгрузка —
route-main-all-instructions.json. Effect240/bump42/transparent681instructions
также проверены по фактической длине. Pseudocode main914lines сохранён двумя
страницами draw-main.json/tailoffset740. Ни один input EXE не исполнялся.

## Восстановленные решения

scripts/native/client455_character_draw.{h,cpp},core.cpp,internal.h;
RFClient455CharacterDraw.lib,8public C APIs. Официальные D3D9 interfaces и
собственный typed context; это не восстановленный private class/global ABI.

- Main сохраняет phase/previousDWORDtick, first-tick sentinel и wrap subtraction.
  Scroll5135 и tick5139 обновляются только при положительном effect speed180.
  x87 math сохраняет signedFILD+conditional2^32, а не подменяет его FILDQWORD:
  это важно при PC24. Сравнения float также x87, независимо от SSE DAZ/FTZ.
- Подтверждён cdecl effect(device,stage,type,color,scroll): ровно5stack arguments.
  Decompiler ошибочно добавлял EBX/EDI/ESI и ещё3stackargs. Его apparent matrix+3
  overread в case4 — неверное отслеживание ESP после pushEBX, не реальный overread.
- Environment matrix из BF8360: diag(.5,-.5,1,1),translation(.5,.5,0). Type1/stage0
  не пишет constants; type2 пишет scroll вelement9, type3 заменяетelements1/4 на
  cos/sin(float angle). Type4: bump states иc92matrix сdiag color/2147483264,
  element9=scroll. Type5 ничего не пишет; default очищает texcoord/transform flags.
- Material path сохраняет LIGHTING изeffect196. При выключенном lighting заново
  формируется material: doubled diffuseRGB повторяется вambient, alpha1,прочее0.
  При включённом — копия model material, изменение specularRGB/alpha иpower по
  mesh5579..5591. Это не изменение ambient. Второй pass имеет отдельную material copy.
- Secondary selection использует0/6/4 поtype; primary type4 отдельно меняет
  textures исохраняетprogram0. Normal/bump выбирает1, normal/specular —2;
  texture slots0..5 иstate order сохранены. Само наличие grade5799 без bump/specular
  не переводит управление в соответствующую ветку, как в original.
- Alpha/frequency/special160 route формирует packet2060; second188 может сначала
  рисовать base и только затем отправлять второй pass. Для второй deferred palette
  translation override не применяется, как в original.
- Queue1024 хранит first palette*sortView depth и сортирует far-first. Equal depth
  вставляется перед существующим. Сравнение учитывает unordered через x87 C0:
  NaN не был заменён обычным C++ less. При заполнении packet отбрасывается.
- Transparent выбирает6 дляeffect2, иначе11. Непосредственно перед INDEXED draw
  снова выбирается11 независимо отeffect2: необычный original порядок сохранён.
  Материал использует alpha packet, special+frequency0 задаёт.5. Blend mode,
  material18/19 иskinpalette передаются в original порядке; потом queue reset/shader−1.
- Mesh batch использует5595/5675arrays,5755capacity,5759count:20×10records2000
  и20×10materials68. После200 main рисует mesh сразу. Flush сохраняет original
  FVF278/282, transforms0..3 identity затем captured palette,material/texture/cull.
  Связанный source mesh destructor освобождает все40allocations.
- CPU92DB60 работает только при4bones/count<2048, использует первые4matrices,
  weight4=1−sum3. Normal намеренно проходит Vec3Transform сtranslation ибез world.
  Порядок суммирования сохранён; output global scratch2048×32bytes постоянный,
  включая count0 nonnullpointer. FVF274/DrawPrimitiveUP32 затем278; count2048
  подавляет draw, но сохраняет restoration. Другой bonecount сразу возвращается.
- Shadow используетprogram3, palette иshared/batch ветку. Высокоуровневый culling
  wrapper иsimple92E140 пока не перенесены. Orthographic projection вызывает
  D3DXOrtho иобязательный внешний publisher8C2A90 (scene frustum,не Character).

## Проверка и границы доказательства

16targeted scenarios,185assertions отдельно и внутри полного client lab:
effect matrices/no-write/default,queue ordering/ties/NaN/cap1024,обычный/scroll/
bump/specular/second pass,alpha/frequency,hiddenmesh,DWORDrollover,shadow,CPU count
boundary,200batch records/201st immediate fallback. Material дополнительно проверен
по реальному GPU-пикселю: ambientred/blackdiffuse даёт exactly00FF0000; одной
проверки GetConstantF для утверждения об отрисовке недостаточно.

Реальная пара BELPHEGORHOLIDAY повторно проходит BN→MESH08→ANI→pose→main source
draw→transparent flush.46geometry parts/44skinned,кадры160/2160,3realDDS;
92actual main submissions,9103/9421readback pixels. Main теперь выбираетshader
иmaterial сам: harness больше не выполняет per-mesh draw вместо него. Камера
по-прежнему тестовая; game camera/visibility/culling/runtime frame parity не приняты.

Провайдер D3DX9_36 SHA
`c12f0ab0338eb5031d3d04beaf7208ac848f7e037d21ff963d2af90221cbe935`;
HAL/SOFTWARE_VERTEXPROCESSING|FPU_PRESERVE. Два frame SHA совпадают standalone/fullclient
и прежнему related primitive path для этой модели:
`51120a6c3c880b24c72236bcd14e8c35753078d42c2f4272c7c47f49c5a246c7`,
`d641896b979a3af37710ec7cec3a7ca5b9db43876b904365692a66984623d36e`.
Preview work/m9/3a7ddb01/client001/route-frame-{0,1}.bmp. COM/heap/Dmalloc0,
gameDLLs не загружены. Fullclient195TUs,8actual E8REL32 APIs/provider/RVA записаны.
Related primitive source изменён только выделением raw pool branch: второй pass
original вызывает её даже при CPU-retained data. Его596checks/старые кадры прошли.
Большие ANI/format/texture/shared-buffer/Platform01 runtime suites не повторялись.

Существенные ограничения не скрыты:

- В original bump ветка читает material scratch без его инициализации в этой ветке.
  Сохранён последний определённый material basic-ветки; для самого первого bump
  source явно использует zero seed. Эквивалентность неинициализированного стека
  не доказана. Аналогично CPU temporary vectors при zero weights имеют zero seed
  вместо неопределённых первых stack bytes. Это открытые fidelity domains.
- Trig providers обязательны. Lab явно использует modernMTsin/cos(double)→float;
  это не доказательство битового равенства original static __CIsin/__CIcos.
- Guard >30 capturedbones/invalidcontext/OOM возвращает own error; original мог
  повредить память/упасть. Все unsafe/NaN/unmaskedFP/allocator/unwind/errorUI domains
  иполный private ABI не приняты. Secondary flags/visibility/device lifecycle ещё открыты.
- Batch/shadow/CPU synthetics проверяют выбор исостояния; они не являются игровыми
  эталонными кадрами всех этих путей. Common model draw имеет настоящий GPU readback.

Gate inventory/client455-character-draw-checkpoint.json. Normal runtime всё ещё
D3D8/legacy Character:unused source stripped,291modernCOFF/MT/прежний engine archive,
snapshot character455-route-final равен character455-draw кромеtimestamps.
Следом: typed normal Character/model/animation interface audit, wrappers/culling/
simple draw исовместная D3D9engine migration. M6/M6F/M7/M9 открыты.

Воспроизведение через scripts/Invoke-Python.ps1:
audit_client455_character_draw.py → build_client455_draw.py →
probe_client455_draw.py → build_client455_character_draw.py →
probe_client455_character_draw.py → prepare_client_build.py →
probe_client_character_build.ps1 [normal/-HelperLab] →
probe_client455_character_draw_client.py → audit_client_executable.py --label NEW →
checkpoint_client455_character_draw.py. HAL/MSBuild в разрешённом user context.
