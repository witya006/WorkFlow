# Source Character455: состояние, палитра и отправка меша

2026-11-05. M6 в работе. Получен связанный source draw реальной модели с анимацией
и текстурами на D3D9 HAL, отдельно и внутри полного client lab. Это восстановленные
примитивы основного draw; весь92E5F0, эффекты/прозрачность и normal renderer ещё открыты.

## Эталон

PE x86, image base0x400000. Current SHA-256
`b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`;
backup `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.
Семь диапазонов равны обоим pin; размеры/хеши в client455-draw-reference.json.

| VA | RVA | Назначение |
|---|---|---|
| 91CDE0 | 51CDE0 | Начальные состояния Character |
| 91D120 | 51D120 | Палитра skin/pose × world |
| 91FB90 | 51FB90 | Выбор VS/PS и публикация выбранного индекса |
| 92D830 | 52D830 | Константы ambient19 → diffuse18 |
| 92E140 | 52E140 | Один caller ветки shared-buffer draw |
| 92E5F0 | 52E5F0 | Основной draw, пока reference, не полный source |
| 934D60 | 534D60 | Вызов D3DXMatrixMultiply, без transpose |

Raw MCP в ignored artifacts/character-animation455/draw-*.json. draw-main.json
содержит первую страницу752строки; draw-main-tail.json offset740 содержит остаток.
Всего914строк; страницы перекрываются на12. Не принимать первую страницу за весь draw.
draw-main-insn.json начинается с instruction offset600. draw-contract-insn-1.json —
полная палитра. Owned96152de8 закрыта/save. Входные EXE не исполнялись.

## Восстановленные контракты

scripts/native/client455_draw.{h,cpp}:5C APIs, RFClient455Draw.lib, x86/MT.
Используются собственные borrowed logical owner views и официальные D3D9 interfaces,
без приведения старого renderer/Character к новому ABI.

- Начальные render/texture-stage/sampler states повторяют91CDE0. Mode2 выбирает
  declaration36/1weight, mode4 — declaration64/3weights. Direction из light104+64
  передаётся вc10. Полный renderer light104 owner/setter этим не восстановлен.
- Renderer+33836 управляет specularEnable. При ненулевом значении пишутся именно
  numeric states29/146/143: SPECULARENABLE, DIFFUSEMATERIALSOURCE=MATERIAL,
  NORMALIZENORMALS=TRUE. Это не fog states. Нулевой флаг оставляет их прежними.
  FOGENABLE выключается в конце независимо от флага.
- Shader selection всегда делает VS→PS, даже для повторного индекса. ПриFFFFFFFF
  или index>=count оба shader pointers становятсяNULL, но выбранный индекс сохраняется.
  Selection tracker отделён от shader manager known prefix28; это не его полный ABI.
- Material68 передаёт первые4float вc18, следующие4float вc19, в порядкеc19→c18.
- Для каждого mesh bone берётся skin646+64i и умножается слева на world. При count0
  используется pose4830. Transpose отсутствует. Optional второй world заменяет только
  translation float12/13/14 результата; остальная часть остаётся от первого world.
  При count0 одна матрица повторяется вc100/104/108/112; иначе c100+4i.
  Reference count не ограничивается30: возможные ошибки register capacity не скрыты.
- Shared VB привязывается с offset0; start/min vertex = byte remainder блока2300000
  /36 или /64. IB remainder блока1000000 /2. Индексы уже rebased при загрузке:
  BaseVertexIndex всегда0. При indexFFFFFFFF используется DrawPrimitive;
  иначе DrawIndexedPrimitive, triangle counts из vertex5086/index5090 /3.
- SubmitShared требует NULL mesh4506: CPU-retained маршрут92DB60 отдельный. Он явно
  отвергается D3DERR_INVALIDCALL, не считается нарисованным. Count0 даёт S_FALSE.
  Это собственная граница API, не утверждение о return behavior всего original draw.

## Проверенный связанный путь

audit_client455_draw.py использует ранее закреплённую пару9: BELPHEGORHOLIDAY.bn,
MESH08sample010.msh (51part) и sample016.ani. Три требуемых looseDDS скопированы
из Character/Monster/Tex в ignored work/client-reference/draw455/tex с хешами.
Header содержит старые абсолютные D: paths; loader берёт basename. Перезаписи
исходной установки нет. Формат/ANI/bulk corpus заново не тестировались.

Native probe загружает BN→MESH08, ANI→root, выполняет source pose для root/child,
refreshes real texture pointers, вызывает source palette/material/program/shared draw.
Из51parts46 содержат geometry,44 используют bones. Два кадра:160 и2160. Получены
92real palette uploads,92real draws и4аналитических draw (36/64 × indexed/nonindexed).
Во всех четырёх analytic draws vertex offset ненулевой и indexed data уже rebased;
получен одинаковый белый треугольник. Отдельно проверены program invalid selection,
material readback, nonsymmetric skin/world, translation-only override и count0 repeat.
Всего596assertions; проверки slot bounds агрегированы по мешу, не по каждому float.

Провайдер — закреплённый SysWOW64 D3DX9_36 SHA
`c12f0ab0338eb5031d3d04beaf7208ac848f7e037d21ff963d2af90221cbe935`.
D3D9 HAL с SOFTWARE_VERTEXPROCESSING|FPU_PRESERVE, скрытое собственное окно256×256.
Сохранённые GPU readback содержат9103/9421pixels модели. Два кадра визуально просмотрены:
модель с крыльями/текстурами меняет позу. Камера подогнана по первой source pose,
для наглядности Zup переведён в экранную вертикаль. CullNONE/общий basic shader —
политика harness. Это не восстановленные game camera/light/visibility/effect dispatch.

Component/fullclient native outputs и оба frame SHA совпадают:
`51120a6c3c880b24c72236bcd14e8c35753078d42c2f4272c7c47f49c5a246c7`,
`d641896b979a3af37710ec7cec3a7ca5b9db43876b904365692a66984623d36e`.
Preview: work/m9/94e327e9/client001/character-frame-{0,1}.bmp.
COM device/API release counts0, tracked heap0, client Dmalloc balance0,
gameDLLs отсутствуют. В полном проекте194clientTUs; five actual E8REL32 APIs
проверены через RFClient455Draw:draw.obj. Gate client455-draw-checkpoint.json.
Нормальный клиент291modernCOFF/MT, unused APIs stripped, renderer ещё D3D8;
snapshot character455-draw равен прежнему shaders snapshot кроме timestamps.

## Продолжение

Следом восстанавливать весь92E5F0: primary/environment/bump/grade program choice,
material/alpha/texture scrolling, затем отсортированный930A40 и deferred batch92D9D0.
92D3E0 effect constants/92D330 и92D6C0 sort key ещё требуют проверки инструкций:
decompiler показывает неверные register/stack arguments, нельзя копировать его prototype.
CPU-retained92DB60, shadow930120 и wrapper culling9238A0 также открыты.
Только затем переносить normal typed model/animation/draw вместе. Нет shadow records
или rawcasts old280/name4/ID260 →455284/name5/ID264.
Device loss/reset, failure UI, full lighting/camera/effects/runtime comparison и остальные
области M6/M6F/M7/M9 не закрыты. Статус feature029 — partial.

Воспроизведение Python через scripts/Invoke-Python.ps1:
audit_client455_draw.py → build_client455_draw.py → probe_client455_draw.py →
prepare_client_build.py → probe_client_character_build.ps1 [normal/-HelperLab] →
probe_client455_draw_client.py → audit_client_executable.py --label NEW_LABEL →
checkpoint_client455_draw.py. HAL и MSBuild запускать в разрешённом user context.
