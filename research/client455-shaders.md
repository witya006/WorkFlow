# Штатный shader bootstrap Character455

2026-11-05. M6 в работе. Это восстановление исходного D3D9-пути455, без графической
модернизации. Normal renderer/Character draw и M6F/M7/M9 ещё открыты.

## Почему изменён порядок normal integration

Проверенные объявления old SDK: ChAnimation280, name4/ID260/extra276;
AnimationManager24; CHARACTEROBJECT776, count528/meshes532/frame668;
ObjectMesh1072. Эталон455: animation284, loading4/name5/ID264/extra280;
manager4028; character1188, count532/meshes536/frame672; mesh5803.
Основания: static_assert в work/recovered/character-legacy/include/Character.h,
inventory/character-header-recovery.json и предыдущие455reference reports.
Подмена только менеджера передаст старым consumers другое представление данных.
Требуется связанный перенос typed Character/model/animation/render consumers.
Shadow-копия старых records или rawcast между этими типами не добавлялись.

## Эталон и восстановленная логика

PE x86/base0x400000. Current SHA-256
`b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`,
backup `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.
Девять диапазонов равны обоим pin; размеры и хеши в
inventory/client455-shaders-reference.json.

| Роль | VA | RVA |
|---|---|---|
| Character shader bootstrap | 91FD40 | 51FD40 |
| Append program quartet | 939BB0 | 539BB0 |
| Release program/declaration arrays | 939D00 | 539D00 |
| Constructor known prefix | 93A160 | 53A160 |
| Manager/global declaration teardown | 93A1F0 | 53A1F0 |
| Compile/create program | 93A350 | 53A350 |
| File selection/decode/sections | 93A6A0 | 53A6A0 |
| Load wrapper | 93A8F0 | 53A8F0 |
| Strip last extension | 93A9D0 | 53A9D0 |

File loader сначала заменяет последний extension на .sho и пробует его. Если файл
открыт, fallback на .shr не производится даже при неверном содержимом. .sho
XOR-декодируется ключом137bytes:134bytes из VA B39918/RVA739918 и3нулевых байта,
как в инструкциях. Затем NUL termination и case-sensitive strstr по
`[vertex shader]`/`[pixel shader]`; оба pointers найдены до изменения разделителей.
Маркеры обнуляются, CR/LF после них пропускаются. Preamble до маркеров не является
автоматическим общим shader header. Необязательный внешний prefix присоединяется
к каждому stage без дополнительного separator. Line offsets посчитаны, но не
передаются D3DX compiler в выбранном теле.

Компиляция через D3DXCompileShader: entry main, VS vs_2_0, PS ps_3_0, flags8008,
defines/include=NULL. Source string передаётся по data(), не адрес структуры
std::string: decompiler ошибался в этом аргументе. Device CreateVertexShader
HRESULT проверяется, CreatePixelShader HRESULT игнорируется, но требуется pointer.
Program record16 = VS/PS/VSconstantTable/PSconstantTable. Capacity начинается8,
при заполнении удваивается; known owner prefix28 содержит borrowed device и два
динамических массива. Полный private manager class/selection fields этим не заданы.

Bootstrap создаёт D3DXSprite, освобождает старые declaration64→36, создаёт обе
декларации, очищает shader programs и последовательно загружает12фиксированных
имён. Corpus содержит12VS и3PS, а не24stage:9программ vertex-only. Декларации64/36
совпадают с ранее восстановленными96bytes; BLENDINDICES64 — SHORT4@24.

Release обходит program records, внутри каждого VS→PS→VSconstantTable→PSconstantTable,
затем declaration array; pointers/count/capacity сбрасывает, borrowed device сохраняет.
Shader compile failure после успешного VS оставляет VS/VSconstantTable вне manager.
Это поведение сохранено; test сначала наблюдает2stranded COM objects, затем отдельно
освобождает их. Source не скрывает эти reference leaks автоматическим cleanup.
При vertex-create failure source также сообщает оставшиеся code/error buffers.
Эта ветка не проверена физическим отказом GPU; OOM/unchecked failure не сертифицированы.
Modal error MessageBox/engine logging ещё не подключены: ошибки доступны вызывающему
через diagnostic. Повторный sprite bootstrap сохраняет исходный порядок вызовов,
но его failure/device-reset lifecycle ещё не принят.

## Source и выполненная проверка

scripts/native/client455_shaders.{h,cpp}, generated shader_key.h:7C APIs,
современный x86/MT archive RFClient455Shaders.lib. Только собственные logical
owners и официальные D3D9/COM interfaces, без cast старого D3D8 renderer.
SHO/raw decoded HLSL остаются под ignored work/, в Git только код/ключ/хеши.

4Python parser tests:12real inputs, reversed sections, CR/LF, пустые/обрезанные
маркеры, embeddedNUL, case sensitivity. 119native assertions standalone и
full-client own entry:12real SHO,12VS+3PS,2actual D3D9 declarations, GetFunction
сравнивается с настоящим compiler bytecode; actual compiler input SHA совпадает
с15независимо извлечёнными stage. Проверены file priority/plaintext fallback,
capacity16, binding, teardown и observed failure leak. Provider — именно
D3DX9_36 SHA `c12f0ab0338eb5031d3d04beaf7208ac848f7e037d21ff963d2af90221cbe935`.

Один harness DrawPrimitiveUP использует original sh_basic, declaration64 и
synthetic weighted vertices64 с identity palette. Readback даёт белый треугольник
на чёрном фоне; source и fullclient frame SHA равны
`61648d3a33bf95fce248b7fbfb7ebad85e7067d264ef0c6238e5258933808c44`.
Это проверка shader stream/rasterization, не восстановленный DrawCharacter,
не реальный анимированный персонаж и не сравнение с выполнением входного EXE.
Обе COM release counts=0, Dmalloc balance0, gameDLLs не загружены.
Preview: work/m9/4dc80db8/client001/shader-frame.bmp, визуально просмотрен.

Normal snapshot character455-shaders:2451456B/entryRVA1BC450,
SHA `87db29ad1a4461bbaea2c617633b9eb8df1fb445abc394eea538dd8272cf4253`.
Normal source APIs unused/stripped; runtime равен предыдущему manager snapshot
после исключения timestamps,291modernCOFF/MT/тот же engine archive.
Lab193clientTUs,5291520B/entryRVA8A6C,
SHA `4dc80db8f12e9346ed40beef6f12061fd1917607cebb300d72874e7e3f7e29d1`.
7actual E8REL32 callers/provider/RVA в client455-shaders-link.json.
Старые большие ANI/texture/sharedGPU/Platform01 suites не повторялись.

Gate inventory/client455-shaders-checkpoint.json; raw render-*.json и
renderer-start-*.json в artifacts/character-animation455. Owned95159529 closed/save.

Следом: full DrawCharacter/mesh draw/state/constant palette/material/effects,
shader selection и normal typed consumer/platform D3D9 migration. Device loss/reset,
original CPU/FPU/compiler conditions и error UI остаются открыты. M9 не достигнут.

Воспроизведение через scripts/Invoke-Python.ps1: audit_client455_shaders.py →
test_shader455_sources.py → build_client455_shaders.py → probe_client455_shaders.py →
prepare_client_build.py → probe_client_character_build.ps1 [normal/-HelperLab] →
verify_client455_shaders.py [--lab] → probe_client455_shaders_client.py →
audit_client_executable.py --label NEW_LABEL → checkpoint_client455_shaders.py.
