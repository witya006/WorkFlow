# M5: loader helper SPT и первый native data probe

Работа только над клиентом. M5 продвинут, но ещё не закрыт: проверена CPU-часть
выбранного участка, обычная загрузка карты и численная эквивалентность x87 эталону
ещё не доказаны. M9 остаётся активной целью.

## Привязка к 455

Оба закреплённых x86 PE, base 0x400000:

- current SHA-256 b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b;
- backup SHA-256 46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.

Loader VA 0x90BBF0 / RVA 0x50BBF0, 1318 bytes,
SHA-256 a8c404bd7b22e72091b8f34453cb224ad11f14d0ab71074bcc19618051df27a4.
Сопоставление основано на всём алгоритме, полях, выделении памяти и вызывающем
коде, а не только строке -node_tm. apply_client_helper455.py проверяет полный body
и конкретные инструкции на обоих PE; evidence хранится в behavior ledger.

Реальная ветка загрузки уровня: 0x8EA220, создание имени EXT.spt в 0x8EAA60–70,
вызов loader 0x8EAA88 с this=level+512. Затем указатель передаётся в объект BSP
по +744 (0x8EAA93). Старый CLevel::LoadLevel также строит EXT.spt и вызывает
mDummy.LoadExtDummy, но указанной дополнительной связи BSP в старом коде нет.
Её дальнейшее использование пока не восстановлено. Не выдавать ручное чтение
всех .spt за доказательство, что уровень автоматически выбирает каждый из них.

Смежные подтверждённые функции: ctor 0x90BA40/RVA0x50BA40; GetDummy
0x90BA60/RVA0x50BA60 (clamp к последней записи), bbox 0x90BA90/RVA0x50BA90,
GetDummyList 0x90BB90/RVA0x50BB90. Bbox использует transform
0x8C0980/RVA0x4C0980 и inclusive bounds 0x8BBE60/RVA0x4BBE60.
Inverse 0x8BFBC0/RVA0x4BFBC0 соответствует cofactor-алгоритму старого MatrixInvert:
проверяет affine-last-column с порогом .001, записывает translation inverse;
защиты от нулевого determinant не обнаружено. Для singular/NaN parity нет.

## Восстановленные различия

Отдельная опция RF_CLIENT_455_HELPER_LOADER, default OFF, driver явно ON.
Оригинальные байты/ветки сохранены, compiler-only patches не смешаны с behavior.
Рабочие extdummy.cpp/.h изменены без перекодировки, originals не изменены.

1. После fopen, до проверки его результата, mNum=0; при отсутствующем файле
   capacity/pointer сохраняются. Release по-прежнему освобождает retained pointer.
2. Каждый следующий *name проходит strlwr. В старом коде goto попадал после
   strlwr и последующие имена могли сохранять регистр. Прежнее общее описание M3
   о нижнем регистре всех имён старым loader было неточным и исправлено.
3. -interior устанавливает mFlag|=4, помимо music=1/fog=2.

Layout одинаков: owner12; record208: name0[32], flags32, bbox36/48, id60, args64[16],
matrix80[64], inverse144[64]. Native static_assert подтверждает современный layout.
Initial capacity16, growth+32; name ограничено31bytes. Опции внутри записи
сравниваются с учётом регистра; общей нормализации всех option tokens нет.
Нет -node_tm: mMat identity, inverse остаётся нулевым. Fog color сбрасывает start/end
на значения состояния движка; порядок опций важен. Reload-success не освобождает
старую память; это не исправлялось. Небезопасные malformed paths не сертифицированы.

## Native проверка

probe_client_character_build.ps1 -HelperLab собирает все 180 старых client C++ + own
lab entry и 58 engine C++, в отдельном build-helper-lab. Обычный WinMain сохранён
как _RFOriginalWinMain@16 и принудительно удержан linker /INCLUDE. Новый WinMain
принимает только --rf-helper-probe. Он вызывает настоящие CExtDummy методы из
того же R3EngineClientMT, читает записи, использует matrix/inverse для ненулевой
точки внутри bbox и точки снаружи, проверяет flags list/clamp/invalid-index/release.
Это лабораторный вход полного проекта, а не обычный запуск игры/LoadLevel.

Исходные игровые EXE и DLL не запускались. Miles/ABuse/Adv/PDLL — delay imports;
перед тестом и после него GetModuleHandle проверяет, что они не загружены. В lab
и рядом с EXE нет DLL providers. Остальные прямые imports — Windows. Нет графики,
игровых файлов фильтров, сети или normal game teardown. Свои ресурсы освобождены
явно; ExitProcess исключает ошибочный teardown неинициализированной игры.

Native EXE SHA-256 7f5d7be0679cce3c92eff3f6ec176c99b444c67758805731f415cb6493df0b5a,
x86/base0x400000, entry RVA0x9ADE. Snapshot work/client-helper-lab/RF_Online.bin.
Сводка inventory/client-helper-runtime.json; build/source hashes в
inventory/client-helper-lab-build.json. Большие outputs/input copies ignored.

140 закреплённых реальных файлов / 97 543 записи прошли native загрузку и проверки
имени/bbox/matrix/default bytes. Среди них 23 EXT.spt с 48 записями; часть имён
с подчёркиванием не следует автоматически считать выбранными текущей картой.
12 собственных scenarios /276 records: count0/1/15/16/17/47/48/49/80, long uppercase
names, пустое имя, -interior/music/fog/id, порядок/defaults fog, no-node identity,
отсутствующий файл после загрузки, отсутствие script_begin, пустой input.
Всего 2 546 779 native/comparison assertions; это не процент полноты клиента.
4 unit tests проверяют маленькие PE import/delay tables и повреждённые границы.

Фактические world/local scalar outputs совпали побитно с независимым binary32
расчётом. Matrix*inverse проверен с absolute tolerance .00005 для linear части,
.03 для translation; максимальная observed world->local ошибка .001953125.
Все выбранные внутренние точки классифицированы внутри. Это НЕ сравнение с
исполнением x87-кода 455 и не доказательство его точных rounding/NaN/locale правил.

## Обычная сборка и продолжение

Обычная RF_Online.bin также собрана с helper455 flag и без lab entry/delay switches.
2 436 608 bytes, entry RVA0x1BAA10, SHA-256
cf6cd16e348453dfeb478cfa06947acdb3749332ca102cc78991f43f8f120f1d.
Snapshot artifacts/client-first-build/helper455, inventory/client-first-build.json.
Все 284 modern objects x86 /MT, прежние draw/logger/login selections проверены.
Обычный EXE не запускался. Первые initial/clean snapshots сохранены без изменений;
новая ревизия не выдаётся за повторную clean-проверку исходного EXE.

Далее: точное численное сравнение выбранных math contracts с 455, проверить
полный клиентский путь использования EXT helpers/BSP и только затем закрывать M5.
OOM, длинные/не-ASCII tokens, небезопасные malformed inputs, повторная успешная
загрузка, fog rendering и новая BSP/interior связь остаются открытыми.
