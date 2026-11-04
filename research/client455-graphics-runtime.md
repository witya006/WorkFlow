# Первый реальный GPU-путь клиента

Получен рабочий hidden-window graphics entry полного клиентского проекта: genuine
InitR3Engine/R3InitDevice, CEntity, CParticle и CLevel::LoadLevel/FrameMove/render/release.
Обычный игровой WinMain не запускался; входные EXE не исполнялись, серверы не затрагивались.
Это legacy D3D8 backend с восстановленным selected455 data path, не полная графическая
эквивалентность D3D9 клиента455. Модернизации графики нет.

## Выполнение и данные

Own lab entry --rf-graphics-device/entity/particle/level создаёт hidden window640x480
с WS_EX_NOACTIVATE и windowed D3D8 HAL,software VP flag0x20,lockable X8R8G8B8 backbuffer.
Окно не показывается/не фокусируется, мышь и клавиатура не используются. Адаптер,
возвращённый API: NVIDIA GeForce RTX2080Ti. Sandbox CreateDevice вернул0x8876086A;
та же сборка без ограничения sandbox создала HAL. Исходники для этого не менялись.

scripts/native/client_graphics_lab.inc включён только в диагностический lab WinMain.
scripts/probe_client_graphics455.py сверяет source/EXE/input SHA, использует delay
imports без игровых DLL рядом с EXE/CWD и запускает только собственный проверенный EXE.
MSS32/ABuse/Adv/PDLL GetModuleHandle проверки проходят до/после каждого сценария.
Звук не инициализируется; существующие guards в engine sound routines возвращаются
до Miles calls. Sound/backend/network/normal startup не объявлены проверенными.

Используются unmodified copies RPK и map resources под work/client-graphics-lab/<hash>/.
Для двух normal-map cases скопированы все78MapEntity archives, целые каталоги lobby
и Platform01; список реально закреплённых inputs с SHA находится в runtime report.
Другие server/client installations не изменялись. Original reference EXE не запускается.

## Результаты

Итоговая own lab SHA-256
ece2acccb434ef06ee0aba3d35a15778f3bdf87e5b70589221f8f34732aed3ae.
13cases/321native checks,0failures/warnings/errors. Во всех cases Dmalloc balance0,
final device/D3D COM reference counts0. Кадры читаются из настоящего GPU backbuffer
через LockRect; BMP framing и число пикселей, отличных от clear color, независимо
проверены Python. Изображения просмотрены. GDI screen capture не используется.

| Сценарий | Факт |
|---|---|
| Device | настоящий HAL,clear/readback,release |
|5real entities | R3E/R3M/R3T из RPK,static vertex/index buffers и GPU texture/render |
|5real particles | реальные SPT,CPU vertex geometry+GPU textures,240RealLoop steps и DrawCParticle |
| lobby | actual LoadLevel,403leaves/402nodes,75visible material groups |
| Platform01 | actual LoadLevel,14141leaves/14140nodes,23helpers/8interiors,12visible groups из выбранной позиции |

Particle scripts: magmadust150,cora_cir_light40,fe15,fe2 500,snow800 elements.
После240steps1/60s live counts:150,9,15,500,267. Seed rand=1; Noise1 всё ещё использует
реальный GetTickCount, поэтому pixel hash/trajectories не объявлены каноническими.
Первый Cora probe дал пустой кадр: test entry не задал caller-owned mRotMat.
Исправлено только условие теста — identity, как задаёт weather owner; production
particle код не менялся. Итоговые пять particle frames имеют видимые pixels.
Collision-capable fe2 в standalone particle case имеет mBsp=NULL: её collision parity
этим не проверена. Обычная map entity/render path проверена отдельно.

GPU texture sizes/FourCC совпали с выбранными embedded DDS:128DXT3,256DXT5,128DXT1,
64DXT3,64DXT1. Runtime mip counts8/9/8/7/7; часть файлов содержит6/5levels, поэтому
совпадение file mip count с созданным texture не утверждается. Полный mip behavior
455 остаётся M6-вопросом. D3D9/шейдеры/полное lighting/material parity не проверены.

Кадры и immutable native records сохранены в ignored work/client-graphics-lab:
ece2acccb434ef06/level-lobby/frame-001.bmp и level-Platform01/frame-001.bmp,
также все entity/particle frames. Каждый SHA есть в inventory/client455-graphics-runtime.json.

## Helper consumer через настоящий FrameMove

Platform01EXT.spt загружен штатным LoadLevel; GetDummyList(mask4) вернул8interiors.
Центр первой actual local bbox преобразован настоящим GetWorldFromLocal, затем
IsInBBox подтвердил включение. Для outside30000/30000/30000 проверено отсутствие
попадания во все8zones. Camera/view/inverse view передаются обычному CLevel.

Две реальные weather particles имеют15/500elements. Три FrameMove с нулевым delta
проверили их state tuples: inside/night[0,0],outside/night[1,1],outside/day[0,0].
Указатели helper owner/два слоя/field flags/ночные thresholds из восстановленного
кода участвуют в настоящем map path. Затем обычный render camera и FrameMove
отрисовали scene. Это завершает первый selected helper-data участок M5; остальные
particle options/curves/lifecycle/errors и весь клиент не объявляются закрытыми.

## FPU и эталон

Измеренные x87 control words: initial0x027F,после InitR3Engine0x027F,после CreateDevice
0x007F. После actual model/map loading,до/после draw и во всех трёх helper/weather
FrameMove control word остаётся0x007F. Это наблюдение собственного D3D8 пути на данной
машине. Две helper math функции уже совпадают с617bytes инструкций455, кроме
проверенной absolute epsilon relocation, и проверены в12precision/rounding modes.

455pins x86/base0x400000: currentSHA
b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b,
backup46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.
IDA подтвердил Direct3DCreate9 path0x8F0330/RVA0x4F0330,enumeration0x8EF080/RVA0x4EF080
и CreateDevice0x8EF690/RVA0x4EF690. Все3bodies совпали в обоих PE. В enumeration
записываются VP candidates0x40/0x80/0x20; перед CreateDevice flags OR0x4. Шесть exact
instruction checks: scripts/audit_client_graphics455.py,inventory/client455-graphics-reference.json.
Raw analysis — artifacts/graphics455-analysis. Owned IDA session77bfa3a2 закрыта/save.

Actual runtime x87 state455 после всех startup callbacks не установлен: эталон не
исполнялся. Pixel/physics equivalence всего renderer не следует из этих находок.
D3D8vsD3D9 — обязательный functional restoration gap M6, не optional M8 modernization.

## Повтор и следующий этап

scripts/probe_client_character_build.ps1 -HelperLab,затем через Invoke-Python.ps1
scripts/probe_client_graphics455.py --entity --particle --level lobby --level Platform01.
MSBuild FileTracker и HAL требуют разрешённой escalation вне sandbox на этой машине.
Во время диагностического запуска input game DLL не нужны.

703weather checks и30resource full-project checks повторены на итоговой lab revision.
Один real helper file+12fixtures прошли23 337checks; последняя полная140file audit
остаётся pinned revisione9ae5fa895742de2 и не переименована в новую. Linked math,
resource branches/DDS mask,draw/logger/lobby и286normal x86 /MT objects проверены.
Normal RF_Online.bin a761c930a5ff86025d0a68ab195bd9253855b1d7887f3d9d0f6b9639fec8970c
не менялся и не исполнялся. M6/M6F/M7/M9 остаются открыты.
