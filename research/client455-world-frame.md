# Обычная карта, камера и свет — участок120

2026-11-09. **PARTIAL, M6.** Исправлена ошибочная привязка метода камеры
в119. На настоящей Bellato проверены подготовка кадра, очередь источников,
обычный/магический свет, архивный aiming effect и затухание/удаление.
Остались подтверждённые отличия геометрического светового прохода; полный
рендер, игровые стадии и M9 не приняты.

Текущий gate: [client455-world-frame-checkpoint.json](../inventory/client455-world-frame-checkpoint.json).
Команда: `scripts/Invoke-Python.ps1 scripts/checkpoint_client455_world_frame.py`.

## Исправление119

В119 функция VA8EB7F0 была неверно названа методом обычной карты, а8E7850 —
методом Empty. Это привело к переносу порядка INS в обычный CLevel. Подтверждение
алгоритма отдельной функции было недостаточным: не проверили её владельца через
конструктор и таблицу виртуальных методов. Утверждение119 о предыдущей view
для обычной карты отозвано. Прочие quake/sway алгоритмы этим не опровергнуты.

Настоящий CLand loader7C8600 выделяет584bytes и на7C8703 вызывает8E9F40.
Конструктор пишет vtableB38494. Её slot9=8EA220(load),slot14=8E7910(frame),
slot18=8E7C40(map draw),slot27=8E7850(view). Следовательно, обычная карта
сначала публикует новую/current view, затем считает quake, затем прибавляет
translation к локальной и глобальной матрицам. Исправлены native include и
отдельный Python oracle. Тест меняющихся направлений принимает текущую view.

INS constructor8ECFA0 пишетB3872C;её slot27=8EB7F0,slot9=8ED220,slot14=8EC190.
Именно INS использует предыдущую global view перед publish. INS источник пока
не восстановлен. Наличие ILevel/Empty и общий private ABI этим не приняты.

## Статические доказательства

Pin x86/base400000:
b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b;
secondary46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.
26 полных тел/26 полных asm/2772 инструкции и две204-byte vtables совпадают
между pins. Все E8 calls декодированы из байтов. Декомпиляция используется вместе
с asm; неверно выведенные Hex-Rays register prototypes/Concurrency имена не
принимаются за настоящий ABI или назначение класса.

| RVA | Назначение |
|---|---|
|0x3c8600 / 0x4e9f40|Обычный map owner и CLevel constructor|
|0x4ecfa0|INS constructor|
|0x738494 / 0x73872c|Таблицы обычного CLevel и INS|
|0x4e7850 / 0x4eb7f0|Разные порядки view для CLevel и INS|
|0x4e7910 / 0x4e7c40|Обычные frame/map draw,реальная clear/render цепочка|
|0x4b46e0 / 0x4b46f0|Очистка/число источников|
|0x4b4700 / 0x4b4760|BBox/тип источника|
|0x4b4780 / 0x4b4820|Get/Insert,56-byte записи и hard cap10|
|0x4ff060|CBsp DrawDynamicLights,selection magic/regular|
|0x4c87a0 / 0x4c8bf0|Настройка/сброс texture transforms/samplers/blend/fog|
|0x4fe980 / 0x4fec90|Геометрия regular/magic проходов,известные неперенесённые отличия|
|0x4c4ec0|Декларации D3D9,включая XYZ+D3DCOLOR offset12|

Raw: artifacts/client455-progress/world-frame120-reference.json,
world-frame120-session.json и world-frame120-extra-session.json. Две собственные
IDA94e4ad3e/b2c3029d saved/closed/list0. GetBBox8B4700 был кодом без function
item; на рабочей IDB задан проверенный диапазон8B4700..8B4751. Input EXE не
исполнялись. Серверы не менялись и не собирались.

## Реальные проверки

World run: work/m9/6e19ea9b/world-frame-001. Обычные CLand/CLevel/CBsp,
реальные BSP/EBP/материалы/текстуры Bellato и архивный effect1358041136.
Контролируемая камера смотрит на известный455 tutorial spawn2466,277,-1129;
реальная collision query даёт пол. Это fixture view, не полная игровая камера.
Положение и обе матрицы согласованы; ресурсы скопированы/hardlinked только
из прежних work-копий, SHA входов после запуска не изменились.

76 операций очереди совпали с отдельным instruction-derived oracle: лимиты
0/1/3/10/12,переполнение,уменьшение лимита,zero/negative diameter,полные color/
texture/magic/blend/BBox. Hard cap10 проверяется до сдвига по лимиту: заполненные
10 не принимают новый источник даже после уменьшения лимита. Поведение сохранено.
Миграция queue кода не потребовалась: выбранный legacy source ему соответствует.
Unsafe invalid IDs/corrupt count/overlapping memcpy на всём домене не приняты.

16 измерений настоящего OS clock дали оба знака30fps(-1,+1). Quake с фактическим
dt и этими знаками совпал с отдельным oracle. Это связь provider→consumer;
полный timing всех игровых стадий,allFP/CRT и RNG interleaving ещё открыты.

Пять640×480 GPU кадров просмотрены. Base и post-clear побайтно одинаковы.
От matched clear отличаются151256bytes magic,146637 regular и646571 archivedFX.
Это не сравнение с выполняемым455. 16/16 FX кадров действительно наполняют
очередь после CLevel::FrameMove clear. Native Bind/ValidateDevice успешны во всех
трёх световых примерах:one pass,CULL3,ZFUNC4. Найдено36leaf/811face references,
735upward references; реальная512×512 DXT1 texture сохранена из устройства.
Её alpha255,center не пуст. Геометрия/текстура не заменены тестовыми картинками.
Шесть штатных texture warnings при очистке six-track cue сохранены.

Ранние попытки не считаются приёмкой. ca3298c6 обнаружил NULL default texture:
в комплекте нет System/dlight.dds и target тоже условно сохраняет этот путь;
применяется настоящий texture аргумент из архивного эффекта. ac75be0f сравнивал
неподготовленные кадры после изменения WORLD эффектами — начальный вывод о свете
по разнице с base был недостаточен. После matched prep c6164598/523d92a0/f4cee900/
405ee97f/7234b179 показали отсутствие projected output. Причина была в fixture:
задали view, но не global inverse view, использующийся светом. Исправлено в
сценарии, без обхода/изменения production light behavior. Итог принят только6e19ea9b.

Fresh corrected quake CPU work/m9/11d9e9d7/quake-001:142events/2921exactscalars.
Fresh actual explosion work/m9/21d0f1cc/quake-effects-001:545frames,onset79,
151active,26160exactscalars,реальный CLevel→D3D view. Ещё5 GPU кадров просмотрены;
20штатных warnings сохранены. Самостоятельные fixtures не принимают весь gameplay.

Engine67 7c828f7767bfa5a36ce0d8df2f2f133fc91a235284115c49c75e496a289252e9.
Изменён только level.obj;остальные66members побайтно равны119,без timestamp-only.
Точные119engine9ae6ace8… и ownPE406b400e… сохранены в engine-before120.lib и
normal-before120.bin. Baseline033 сохранён;старый082snapshot всё ещё отсутствует.
Own PE0806b113f1da0025c32dae2b327fefd920a2183fad01437e77b900818f75c9dd,
2225664bytes,x86/base400000/entry167320,WinMainb98b0/afterCreateb9a24;
182client/20kernel/70facade/unresolved0,безCharacterMR/FORCE.
СвежиеANI/BBX consumers,map2692/330/canonical,ownstartup/contracts/window/device/
existingCreate1 проходят. Старые159k/texture649/receiver/Character/bulk не повторены.

## Следующая121 и оставшиеся разрывы

Перенести подтверждённые отличия геометрического света. Regular8FE980:skipAttr0x10,
leaf limit128,face limit5000. Magic8FEC90:skipAttr0x30,positiveNormalY,ширинаBBox
не более1000,оба конца внутри root bounds,сохранить saturation faceindex2999,
triangle batch2000. Обе ветви используют owned CBsp world matrix и explicit
declaration. Legacy implementation отличается;его видимый вывод на данном полу
не доказывает равенство всех guards/batches/флагов и не закрывает renderer scope.

Проверить настоящие writers этой world matrix и CLevel/INS/Empty dispatch до
реализации состояния. Не переносить соседний метод по одному похожему имени.
Полные ILevel/frame/projection/sky/alpha/shadow/device reset/траектории/blur,
input/control writer7E2AD0,Tutorial/Avatar/Login/auth/protocol/Character и прочие
client-acceptance gaps остаются открытыми. M6/M6F/M7/M9 OPEN.
