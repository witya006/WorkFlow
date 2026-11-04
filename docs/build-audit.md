# Статический аудит собираемости — 2026-11-04

## Вывод и границы

УТОЧНЕНИЕ ОБЛАСТИ: работа исключительно над клиентом и его зависимостями.
Ниже сохранены факты прежнего аудита всех 14 проектов; серверные строки — историческая
инвентаризация. B12/B13 не являются блокерами клиента. Прежний выбор LoginServer отозван.

Проверены все 14 DSP, 14 DSW, 41 конфигурация и 832 записи SOURCE. Шесть записей
указывают на отсутствующие файлы, все в двух проектах. Все ссылки DSW на DSP разрешаются.
В 12 проектах все SOURCE существуют; это не доказательство успешной компиляции/линковки.
Ни одна сборка пока не запускалась: рабочий VC6 toolchain не найден.

Отчёт: `inventory/build-audit.json`; генератор: `scripts/audit_build.py`.
Все 962 исходных файла сверены с прежним SHA-256-манифестом: изменений нет.
Исходники не копировались, не перекодировались и не исправлялись во время аудита.

Метод: SOURCE, конфигурации и небазовые ADD/SUBTRACT-директивы DSP, ссылки DSW,
рекурсивные локальные include, pragma comment(lib), import и файлы ресурсов RC.
В отчёте сохранены пути и номера строк. Include-пути и ветки препроцессора объединены
консервативно; глобальные INCLUDE/LIB VC6 неизвестны. Совпадение basename отмечается
как кандидат, а не как разрешённая зависимость. Макросы include, полные правила
поиска заголовков компилятора и пользовательские build steps не эмулируются.
Системные headers/.lib, отсутствующие в репозитории, требуют SDK, но не объявляются
утраченными исходниками. Условные зависимости ниже проверены вручную.

## Матрица всех проектов

Пути относительно legacy_source в config/paths.json. SOURCE включает headers,
ресурсы и .lib. C++ — число перечисленных .cpp. Все цели Win32 x86 по DSP.

| № | Проект / расположение | CFG | SOURCE / C++ | Результат и зависимости |
|---|---|---:|---:|---|
| 1 | R3Engine/R3Engine/R3Engine.dsp | 6 | 126 / 58 | SOURCE полны. DirectX 8 SDK; Character.h для RTMOVIE; JPEG/Miles для зависимых целей. Несогласованность имён и CRT |
| 2 | R3Engine/R3Engine/Util/CameraExporter/CameraExporter.dsp | 2 | 18 / 7 | Нет SOURCE ../Common/d3d.h; legacy DirectX headers. Отсутствующая запись .h ещё не доказывает ошибку компиляции, если include разрешится через SDK |
| 3 | R3Engine/R3Engine/Util/EntityExporter/EntityExporter.dsp | 2 | 31 / 14 | SOURCE полны. Legacy DirectX headers; d3dframe.lib есть рядом с проектом |
| 4 | R3Engine/R3Engine/Util/PreScript/PreScript.dsp | 2 | 15 / 7 | SOURCE полны. Через Common нужны d3d.h/ddraw.h; это не утилита только на CRT |
| 5 | R3Engine/R3Engine/Util/R3Bsp/R3Bsp.dsp | 2 | 45 / 19 | SOURCE полны. DirectX, OpenGL/GLU, отсутствующий GLUT; d3dframe.lib есть; RC использует afxres.h |
| 6 | R3Engine/R3Engine/Util/R3MapExp/R3MapExp.dsp | 3 | 13 / 3 | Нет 5 входов SDK 3ds Max и include-каталога. Release/Debug/Hybrid, выход .dle |
| 7 | R3Engine/R3Engine/Util/R3MRobot/R3MRobot.dsp | 2 | 3 / 2 | SOURCE полны. CRT/Win32 для сборки; при выполнении вызывает ConvMaterial и shell copy/md |
| 8 | R3Engine/R3Engine/Util/SkyBoxGen/SkyBoxGen.dsp | 2 | 33 / 14 | SOURCE полны. Legacy DirectX headers, RC/afxres.h |
| 9 | RF Client Side/RF_Client/RF_Online.dsp | 4 | 359 / 180 | SOURCE полны, но нет Character.h и ряда .lib; include-пути к имеющимся R3Engine headers не настроены |
| 10 | RF Server Side/RF_Server/AccountServer/AccountServer.dsp | 3 | 30 / 12 | Локальные входы полны; Win32, Winsock, ODBC, winmm |
| 11 | RF Server Side/RF_Server/ControlServer/ControlServer.dsp | 2 | 73 / 11 | Локальные входы полны; Win32, Winsock, ODBC, таблицы; не заменяет ZoneServer |
| 12 | RF Server Side/RF_Server/LoginServer/LoginServer.dsp | 4 | 28 / 12 | Локальные входы полны; Win32, Winsock, ODBC, winmm. Вне клиентской задачи |
| 13 | RF Server Side/RF_Server/RF_Server/AccountServer/AccountServer.dsp | 3 | 30 / 12 | Дубликат №10 по исходникам/проектам |
| 14 | RF Server Side/RF_Server/RF_Server/LoginServer/LoginServer.dsp | 4 | 28 / 12 | Дубликат №12 по исходникам/проектам |

## Реестр недостающего и несогласованностей

| ID | Объект | Подтверждение / что требуется |
|---|---|---|
| B01 | VC6 compiler/linker/build driver и SDK | cl/msdev/nmake/rc/link не найдены в PATH; предыдущий vswhere пуст. Поиск cl/msdev/nmake под E:/RFOnlineTrash также пуст. Нужен закреплённый VC6 toolchain; SP6 — стартовая база, не доказанная версия первоначального компилятора |
| B02 | Character SDK | Character.h не найден в исходниках и целевом поиске E:/RFOnlineTrash. Нужен клиенту (baseheader.h:29 и другие), движку — под RTMOVIE (extension/characterobj.h:5–11) |
| B03 | Character libraries | mainapp.cpp:747–753 требует CharacterMD.lib для Debug, CharacterR.lib для Release. Оба отсутствуют. Две CharacterMR.lib идентичны по SHA-256; совместимость символов/CRT/ABI не проверена. Переименование без проверки не решает проблему |
| B04 | Клиентские сторонние .lib | Не найдены JpegLibMT.lib (mainapp.cpp:745), ABuse.lib/Adv.lib (uiglobal.cpp:163–164), ziplibm.lib/ZipArchive_STL_M.lib (cgp_login.cpp:7–8). Нужны зависимости либо отдельно проверенные реализации контрактов |
| B05 | Условная PDLL.lib | protect.cpp:8–14: pragma под __PROTECT_MODE__, задаваемым при отсутствии _DEVELOPER_. Файла нет. Не безусловное требование всех CFG; Developer-поведение требует проверки |
| B06 | R3Engine variants / CRT | Клиент требует R3EngineDMT.lib/R3EngineMT.lib. Client Debug движка создаёт DMT с /MT и _DEBUG, клиент Debug использует /MTd. Выхода R3EngineMT.lib в DSP нет. Имеющаяся R3EngineD.lib не доказана заменой |
| B07 | DirectX development SDK | d3d8.h/d3dx8.h/d3dx8math.h, dinput.h/ddraw.h и .lib d3d8/d3dx8/dinput8/dsound/dxguid. Утилитам нужен также legacy d3d.h. Пригодность версии проверять компиляцией; README рекомендует 8.1, но это не атрибуция |
| B08 | Include-пути клиента | В небазовых CPP-директивах RF_Online нет /I. Многие R3Engine headers есть в 1stclass/2ndclass/common/extension/D3d/include, но из клиентского проекта не разрешаются. Нужны явные пути в копии проекта |
| B09 | 3ds Max SDK | R3MapExp SOURCE: ../../../lib/core.lib, geom.lib, mesh.lib, maxutil.lib и ../../../Include/ipoint2.h отсутствуют. Не разрешаются Max.h/decomp.h/interpik.h/istdplug.h/shape.h/stdmat.h. Версия Max неизвестна |
| B10 | GLUT | R3Bsp требует gl/glut.h и glut32.lib, которых нет в комплекте. OpenGL/GLU — отдельные системные зависимости |
| B11 | CameraExporter header entry | ../Common/d3d.h отсутствует. Установить, предполагалась ли копия SDK header; не создавать пустой файл |
| B12 | Исходная серверная БД | В legacy-дереве нет .sql/.bak/.mdf/.ldf. ODBC wrapper вызывает SQLConnect/SQLExecDirect; для runtime нужны DSN/схема/процедуры. MySQL .sql в GoMMO есть, совместимость не доказана |
| B13 | Полный игровой сервер мира | Среди DSP нет ZoneServer. rfzonedatabase.cpp, протокол и таблицы не составляют подтверждённый сервер мира. Искать дополнительные материалы; клиент не содержит всю серверную логику |

Дополнительные различия:

- LoginServer Release: /MDd и NDEBUG. x2o_Release: _DEBUG, /Od, /MDd, __SERVICE.
  Название Release не доказывает оптимизированную release-сборку.
- R3Engine Tool Debug и S Debug NoSound пишут в один R3EngineDMTDLL_NoSound.lib:
  результаты разных CFG необходимо изолировать.
- R3Engine RTMovie Debug/Release не имеют /D RTMOVIE в CPP-директивах, несмотря на имя.
- cconsoleex.h включается под _CONSOLE, jpegint.h — под JPEG_INTERNALS.
  Активные определения этих макросов в проверенных R3Engine CFG/коде не найдены.
  Эти консервативные находки не являются общими блокерами.
- Miles mss.h/mss32.lib имеются; ABI/версия/runtime не проверены.
- Все 3 непосредственно распознанных внешних RC-ресурса найдены; это не аудит
  ресурсов, которые нужны работающей игре.

## Дубликаты, непроектные файлы и ADO

AccountServer: 11 совпадающих файлов; LoginServer: 13. Различаются только .ncb/.opt/.plg.
В common/network/protocol/database/table двух деревьев совпадают все 116 файлов.
Каноническая ветка — внешний RF_Server; вложенное дерево не удаляется.

26 .cpp не перечислены ни в одном DSP (с учётом копий); список unlisted_translation_units
в JSON. Среди них ADO-обёртки, rfzonedatabase.cpp и обработчики ошибок. Не следует
автоматически добавлять их в сборку.

Четыре #import msado15.dll находятся в rfdatabase.h/_rfdatabase.h двух деревьев и
не входят в найденные include-цепочки проектов. Проектные rfnewdatabase.h/cpp
используют sql.h/sqlext.h и ODBC. На хосте msado15.dll есть в обоих стандартных
Program Files-каталогах; пригодность в будущей 32-битной VM не проверена.
Прежняя общая рекомендация ADO уточнена: для LoginServer подтверждён ODBC.

## Первая сборка: исправленное решение D01C

Выбор LoginServer отменён: сервер не относится к клиентской задаче.
Первая цель — клиентская зависимость `R3Engine - Win32 RTMovie Release`.
В её CPP-флагах отсутствует /D RTMOVIE; это основание проверить возможность сборки
ветки без Character.h, но не доказательство успешной компиляции.

Подготовить VC6/SDK и копии клиента/R3Engine в work/client-build; проверить макросы,
include и CRT, затем две чистые сборки R3Engine.lib. Для .lib анализировать COFF machine,
символы и директивы CRT. Успех архивации ещё не доказывает отсутствие внешних зависимостей.
Возможность использования этой библиотеки клиентом проверять отдельно: RF_Online
требует R3EngineMT.lib/R3EngineDMT.lib. Переименование не заменяет проверку ABI.

Конечная цель — сборка RF_Online после закрытия Character/прочих клиентских зависимостей.
Ни одна сборка в этом этапе не выполнялась.

## Воспроизведение

`scripts/Invoke-Python.ps1 scripts/audit_build.py`

`scripts/Invoke-Python.ps1 scripts/test_audit_build.py`

Пять проверок прошли: комментарии/строки, пути и флаги, отсутствующий SOURCE,
пустой/некорректный вход, реальные проекты/DSW/ADO/целостность. Сканер не заменяет
журнал настоящего компилятора и не сертифицирует собираемость.
