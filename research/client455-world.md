# Настоящие учебные миры BSP39 — участок074

Три карты455 загружены и отрисованы собственным исходным движком через настоящий
CLand. Исправлено владение уровнем при загрузке и освобождение ресурсов в его
деструкторе. Полный ILevel/Tutorial/игровой цикл ещё не принят;M6/M6F/M7/M9 открыты.

## Эталон

455 x86/base400000,SHA-256
`b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`;
backup `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.
10полных диапазонов и48byteprefix CLevel vtable совпали между pins. Сохранены
6полных asm,полная постраничная декомпиляция LoadLevel и связанные owner/camera
методы в ignored artifacts/client455-progress/world074.json.
IDA60286d36 сохранена и закрыта. Оригинальный EXE не запускался.

| RVA | Контракт |
|---|---|
| 3C8600 | Удалить старый dynamic level;выбрать .ins/CLevelIns либо CLevel;загрузить;обновить global и camera |
| 3C7180 | Камера получает CBsp через level virtual4,затем обновляется globalcamera |
| 4E9F40 | Настоящий CLevel наследует ILevel,владеет CBsp и sky |
| 4EA120 | Destructor сначала вызывает ReleaseLevel,затем уничтожает sky/BSP |
| 4E7730 | Release очищает loaded/resources/RTMovie/dummies |
| 4EA220 | Обычная загрузка материалов,BSP,EBP,lightmaps,sky,RTMovie иdummy |
| 4FDEA0/4FF280 | BSP39 header684/EBP20 header388,последовательные записи |
| 4D2EB0 | PlayCamera возвращает view;inverse даёт позицию камеры |

В существующих исходниках уже были BSP39 и EBP20. Переписывать их геометрию на
основании одного возраста исходников не потребовалось. Их реальное использование
на455 раньше не было доказано;теперь есть native загрузка и GPUкадры. Это не
побайтовая/пиксельная сертификация всех методов против оригинального runtime.

## Изменения обычного клиента

client455_land_load.inc заменяет CLand::LoadLevel(char*):удаляет предыдущий
уровень,создаёт новый CLevel,публикует g_pLevel,вызывает загрузку и настоящий
CCamera::Create для привязки к новому BSP. Indexed LoadLevel(BYTE) вызывает тот
же owner path,сохраняя остальные старые effects/radar/time действия как
непринятые области. .ins распознаётся без учёта регистра и возвращаетFALSE:
исходника CLevelIns пока нет,подстановка обычного BSP не производится.

Производный движок получил шестой overlay level.cpp:деструктор CLevel вызывает
ReleaseLevel перед удалением sky/BSP. Базовые source/033library не изменены.
Генераторы сохраняют исходные байты и проверяют предыдущие SHA. Preparation
4E7428C9… повторно получен без изменений. ILevel virtualinterface иinitial Empty
owner пока не мигрированы:sourceCLand.Create по-прежнему создаёт обычный CLevel.
Это явный разрыв,а не утверждение о совпадении private ABI/heap455.

## Реальные данные и результат

| Карта | Вершины | Грани | Leaf | Материалы | Map entities | Высота поверхности в tutorial spawn |
|---|---:|---:|---:|---:|---:|---:|
| Bellato |98020|85661|5455|666|1187|277.230469|
| Cora |108443|126980|8649|477|147|491.476562|
| Accretia |102817|60866|4345|912|0|-296.876953|

Счётчики независимо получены из wire BSP/EBP через map455.py и совпали с native
CBsp. В точках из455 Tutorial найден leaf и GetNextYpos вернул конечную высоту.
Это три реальные collision queries,а не приёмка всей ходьбы/path/collision455.

Native full-object probe использует обычные cland.obj и R3Engine455Startup:level.obj,
реальный D3D9,материалы/геометрию/RPK/текстуры/sky и первый view camera0 из CAM1.2.
На каждой карте выполнены load→frame→opaque GPU capture→reload→frame→capture→
Destroy. Все процессы завершились0,предупреждений0. Шесть640×480кадров просмотрены;
на них видны мир,sky/текстуры/объекты,а не искусственная тестовая сцена. Два кадра
Cora побайтово равны;Bellato/Accretia могут различаться временем движения окружения.
Данные firstCAMview не объявлены целым intro или pixelparity455.

Dmalloc до загрузки и после Destroy одинаков:270592bytes. Загруженный и повторно
загруженный уровень дают одинаковый учёт:Bellato10583464,Cora14343055,
Accretia9627794bytes. Это баланс Dmalloc на этих входах,не доказательство всех
COM/GPU/обычных heap/асинхронных lifetimes. Проверена повторная отрисовка после
замены уровня,а не только наличие флага loaded.

Ресурсы копируются из reference в ignored work/world455-inputs. Запуски получают
hardlinks **только к этим work-копиям**,не к оригинальной установке. В отчётах SHA
всех фактически использованных входов;после запуска проверена их неизменность.
Каждый запуск сохраняет собственные .map и result.json,чтобы следующая компиляция
не уничтожала доказательства. Большие исходные assets и кадры не помещены в Git.

Первые ошибки были исправлениями harness:StripPath требует Windowsbackslash,
RPKprefix должен оставаться штатным .\\Map\\Entity\\,CLand слишком велик для
обычного стека. Ранний99/0xC00000FD исправлен размещением CLand в heap. Геометрия
не подменялась,missing fog assets не заменялись другими файлами.

## Сборка и регрессии

Новая RF_Online.bin:
`fd8b038dcbc0890caf4b728c487dd15448dbcb551a6ed38a804ba7002c8b5c21`,
x86/base400000/entry150790/2043392bytes,182client/20kernel/32facade,0unresolved.
Engine74:67TU/6overlays,librarySHA
`c00d9d4da762dbf226bff5a8110034026159758b41738c4435c30438aa79568c`.
Точная новая PE прошла WinMain/TCP fixture/engine/sound/D3D/Character/existingCreate1.
Актуальные startup contracts,account/Avatar/MainApp иKo/Ru briefing прошли. Старые
большие kernel/GUI suites не повторялись и не помечены fresh.40080201 через
KernelBase остаётся неизвестным first-chance событием. Остановка до обычной игры.

Evidence:client455-world-reference/native(3)/visual/checkpoint.json;gatePARTIAL.

## Далее075

Использовать работающий BSP backend при восстановлении настоящего CGP_Tutorial:
Load/Create,таблица intro segments,frame/input,реальный Avatar иlocalfeedback/
handlers,board/47QBI иfourstagefactory/nextDWORD. Не повторять полный аудит
контейнеров или геометрию трёх уже проверенных карт без новой причины.

Полный ILevel/Empty/INS,всеindexedmapextras,alpha/effects/shaders/lighting/audio,
device-reset/mixedmap transitions,точноеcameraintro,Avatar/world/gameplay,auth/
IME/unsafe/OOM/failure domains остаются открытыми. Успех этих карт не означает
восстановленный полный клиент455.
