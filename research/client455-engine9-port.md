# Начальный перенос настоящего R3Engine на D3D9

2026-11-05. Новая рабочая копия: work/client455-port. Основная проверенная сборка
work/client-build не менялась. В копию перенесены492 клиентских/движковых файла,
50 изменены воспроизводимыми byte patches; кодировки старого текста сохранены.
Новый R3Engine455 собирается из67 реальных единиц x86/MT. Это начало совместного
normal port, не соответствие всего движка455 и не готовый RF_Online.bin.
M6/M6F/M7/M9 остаются открытыми.

Для полного compile потребовались настоящие D3DX9 headers. Локально подготовлен
[Microsoft.DXSDK.D3DX 9.29.952.8](https://www.nuget.org/packages/Microsoft.DXSDK.D3DX/9.29.952.8),
signature Author/Repository проверены dotnet nuget verify. Package/header SHA и
27 извлечённых files — inventory/d3dx9-headers.json. Код package targets не
исполнялся, package runtime DLLs не устанавливались. Заголовки этого пакета
соответствуют June2010 SDK; они не являются доказательством ABI всех функций36.

Для линковки x86 import archive из подписанного package перенаправлен с43 на36:
672 замены одинаковой длины в import descriptors/names, без изменения DLL кода.
Исходный/package/новый archive SHA в client455-d3dx-import.json. Каждый реально
используемый D3DX import имени собственного probe проверен в pinned x86
d3dx9_36.dll SHA c12f0ab0338eb5031d3d04beaf7208ac848f7e037d21ff963d2af90221cbe935.
Итоговый PE импортирует d3d9/d3dx9_36; d3d8/d3dx8/d3dx9_43 отсутствуют.

Основные преобразования основаны на
[Microsoft Converting to Direct3D9](https://learn.microsoft.com/en-us/windows/win32/direct3d9/converting-to-directx-9):
новые COM types, shared-handle arguments, sampler states, stream offset,
BaseVertexIndex в draw call, state blocks как COM objects и отделение vertex
declaration от vertex shader. API соответствие не доказывает поведение455.
Нет aliases IDirect3DDevice8→9 или обёртки, выдающей D3D8 за D3D9.

Шейдерные DWORD handles заменены source RF455R3VertexProgram с отдельными shader
и declaration. Grass declaration соответствует входам штатного455Grass1.vso:
POSITION0/v0, COLOR/v3, TEXCOORD0/v4. Реальный program/declaration создаются наHAL.
Неиспользуемые старые helpers CreateVShader/ReleaseVShader/LoadAndCreateShader
удалены из копии r3d3d8.cpp; их цепочка не имела живых callers. Их замена пустыми
успешными функциями не добавлялась. Остальной shader/state behavior ещё проверять.

Парсер переписывания учитывает вложенные expressions, comments/strings, не теряет
запятую после // comment и отклоняет nonzero старый SetIndices base вместо
недоказанного преобразования. Пять focused tests и компиляция всего engine set
прошли. Во время port исправлены61compiler diagnostics; итог0errors/67objects.
Legacy source и все source changes представлены SHA manifest в ignored
artifacts/client455-d3d9-port/source-migration.json; генераторы/patches в Git.

Собственный engine9-probe запускает настоящие InitR3Engine, R3ConfirmDevice,
R3InitDevice, использует capabilities реального D3D9 HAL, проверяет Grass shader
и подключает source Character455 renderer owner к ТОМУ ЖЕ устройству. Его12
Character programs/sprite/pools/textures проходят создание/освобождение вместе
с ресурсами R3. Это ещё не Character actor draw в обычном клиентском цикле.

Device case прошёл. Затем настоящий CLevel загрузил Platform01, BSP14141leaves,
23helpers,8interiors; оба weather layers дали [0,0]→[1,1]→[0,0]. Карта отрисована
с12visible material groups, frame.bmp просмотрен. Engine warnings/errors0,
Dmalloc до/после0 и device/D3D COM references0. Runtime отчёты содержат immutable
own EXE SHA/entryRVA/output/frame paths. Прошли24device и46map targeted assertions;
не запускались большие неизменённые ANI/model/texture/buffer suites.

При первом map run найден некорректный forward-slash путь в probe: старый
StripPath разбирает backslashes. Исправлен input только тестового запуска.
Затем gate выявил отсутствие helper455 compile option в новой конфигурации;
оно добавлено. Общий список ENGINE_DEFINITIONS теперь используется engine/probe,
включая все восстановленные data/weather/clock/resource ветки. CLand/network
hooks исключены только из engine-only test, не заменены production stubs.
Сбойный запуск не засчитан как успешная проверка.

Граница результата: normal180clientTUs/typed Character/model/animation facade
пока не подключены к этой библиотеке,39старых SDK функций ещё нужно заменить.
Открыты полные camera/state/shader semantics455, resource/error paths,
reset/unwind/stateblocks/fullscreen/display modes. Enumeration пока ограничена
X8R8G8B8; прочие форматы инастройки ещё не приняты. SDK header inlines/полный ABI
36 не сертифицированы. Game455EXE не исполнялся, оригинальные inputs и серверные
файлы не менялись. В кадре own test camera; original game frame parity не доказана.

Gate inventory/client455-engine9-checkpoint.json. Воспроизведение через
scripts/Invoke-Python.ps1: install_client455_d3dx_headers.py,
prepare_client455_d3dx_import.py, test_client455_d3d9_port.py,
prepare_client455_port.py, build_client455_port.py,
build_client455_engine9_probe.py, probe_client455_engine9.py,
probe_client455_engine9.py --level Platform01, checkpoint_client455_engine9.py.
Native builds/runs и загрузка публичного package используют обычную escalation.

Следующий шаг — source Character455.h/facade и реальные consumers180clientTUs
в этой копии. Использовать готовые owner/managers/load/ANI/pose/draw/frustum;
не rawcast старые структуры и не линковать старый CharacterMR ради зелёного link.
