# Память проекта

Обновлено2026-11-09.

117 PARTIAL: восстановлен обычный CLand::LoadData для Map/NDMap110 и
двух дополнительных разделов: 660 подписей,257919 байт изображений. Массивы
588/288/96/84 динамические; реальные maxima54 портала/62 зоны превышают старые50.
UI_SetMinimap получает bounds из BSP node1 и размеры/смещение из map record;
старые8map tables/clamp удалены. Декодированы обычные PE вызовы loader/geometry.
12equalbodies/12fullasm/1850instructions (9new/1284);2IDA sessions savedclosed/list0.
Native2692 PASS: весь canonical output равен независимому reader,330 случаев
геометрии для110 карт на3 реальных BSP node fixtures. Полный BSP load/GPU здесь
не повторялся. Из9 supplied NDMap только zh-tw имеет110;ko-kr100,остальные31
отвергаются точно по count gate,без подстановок. Это подтверждено actual CLand.
Own PEfd8b5070…/entry1670c0/182client-20kernel-70facade/unresolved0/Create1.
Engine67 unchanged;116 runtime gate historical,старые Nuclear/GPU/159k не повторялись.
Full map UI/layer manager consumers/gameplay/texture lifetime не приняты.
M6/M6F/M7/M9 OPEN. Следующая118 — actual texture/ref ownership и20 R3T warnings
последнего nuclear lab116; затем полный world/frame и map UI consumer flow.

## Цель и ограничения

CLIENT ONLY: RF_Online.bin, R3Engine и необходимые клиенту ресурсы/инструменты.
M9 уже определён пользователем: финальная приёмка полного455 без модернизации
графики. Не переуточнять его по старому тексту Goal. M0–M4 diagnostic и выбранный
M5 завершены; M6/M6F/M7/M9 открыты, M8 не нужен. Сборка/Create1/отдельные labs
не являются полной приёмкой. Серверы только справочник, не менять/не собирать.
Оригиналы неизменны, входные EXE не запускать, копии только work/. Local Git,
без remotes/push/publish. Subagents без явного запроса пользователя запрещены.
Python: scripts/Invoke-Python.ps1. Assertions не процент полноты и не AI calls;
не повторять159k/широкие GPU suites без причины. Ignoring не backup.

## Текущее проверяемое состояние

Gate inventory/client455-map-data-checkpoint.json;
scripts/Invoke-Python.ps1 scripts/checkpoint_client455_map_data.py.
Подробности research/client455-map-data.md. Native work/m9/6bbf7812/map-data-001,
2692 checks/110maps/103+7layers/660labels/257919imagebytes/330geometry cases.
Оба потока718859/116750 разобраны полностью; bytes равны независимому reader.
Геометрия проверена на скопированных node1 настоящих bellato/cora/accretia,
не на новом полном BSP load/render. Новых GPU frames0. Обычный PE содержит
CLand.LoadData→RF455_LoadMapData→ParseMapData и UI_SetMinimap→SetMapBound/
SetNuclearMapGeometry455. ApplyMiniMapGeometry455 встроен MSVC в ordinarycaller.
Отказ8 supplied NDMap count31/100 — реальное поведение loader110. Только zh-tw110
совместим с корневым Map110; регион всей установки этим отдельно не доказан.
Два layer раздела пока source-owned data; actual global manager/UI handoff открыт.
Полный MiniMap reset/index/special/avatar/portal/region/scroll/device lifecycle
не перенесён. Безопасный parser guard/atomic failure не доказывает опасные target
read/OOM/overflow/partial-state/reload/leak/private ABI домены.

Обычная сборка:182 client,20 kernel,70 facade,unresolved0,без CharacterMR/FORCE.
PEfd8b507032e9023a284852ff151ec486b413e5568226e0aa2f12be790a5c9ced,
2225152bytes,x86/base400000,entry1670c0,WinMainb98b0,afterCreateb9a24.
Exact own PE startup/device/existingCreate1 PASS;полныйbootstrap/auth/game не принят.
Engine67 unchanged546a7529b51139e856b1a108fcad7849c14b2d00563b7abbfdcc8db10026fa5a;
033baseline существует,082derivedsnapshot отсутствует — старый gap остаётся.

Контракты116 Nuclear factory/all9handlers/MainGame owner/type33 item use/AES
и их доказательства сохраняются в research/client455-nuclear-receiver.md.
116 runtime gate теперь HISTORICAL_NOT_RERUN: receiver101/registry109/aim30/
marker702/message83/20viewedGPU,не свежая проверка117. Последние nuclear labs116
давали20 R3T warnings при teardown;117 не доказывает их устранение или общий
memory balance. Старые Character/world/audio/GUI/159k suites не повторялись.
Снимок gate до изменения: artifacts/client455-progress/
client455-nuclear-receiver-checkpoint-before117.json. Raw analysis и sessions
map117-reference.json/map117-session.json там же; обе IDA sessions savedclosed/list0.

## Следующая очередь

1. Работа118: проследить20 R3T release warnings последнего nuclear lab116 до
   actual455 texture/ref ownership. В старом engine warning не предотвращает
   освобождение. Не подавлять сообщения без доказанного исправления;engine67
   менять только при подтверждённом расхождении и целевой проверке.
2. Полный world/frame/trajectory/camera quake/light/compositing/quality/blur/
   advancedFX/device lifecycle. Затем map UI_SetMinimap/OpenMinimapWindow,
   selected/special/reset/sprite/avatar/portal/region/scroll и два layer manager
   consumers. Geometry-only330 не закрывают эту цепочку. Не менять supplied
   несовместимые NDMap и не подменять110 фиктивными строками.
3. Actual Tutorial/Avatar/Create/camera/QBI47/input/four stage lifetime,
   Login/auth/game flow и полный сетевой протокол. Только клиент.
4. Linker/queue/Macro/Vending/inventory/equip/SF/Animus/Quest/36boards/Trunk,
   остальные Character/action/movement/64-bit status. Все известные contracts
   и gaps сохраняются в client-acceptance.md/feature registry/research.
5. Завершить матрицу M6/M6F, зафиксировать M7 и провести полную M9 приёмку
   клиента455 без модернизации графики;один build/Create/component lab не достаточен.

## Сохраняемые особенности и gaps

Nuclear record32:handles0/4/8,pos16,countdown28,DWORD12 неинициализирован/не читается.
Reset сохраняетposition/countdown,отвязывает launch/impact,останавливает radar tag2
доFX;RadarOff делаетFX доaudio дажеhandle0. Remove/Reset сбрасываетpending даже
безrecords. Pending0 сохраняетaim FX;Reset неaim.Clear. Clock1012850/1012854
процессный,не сбрасываетсяClear,первый ascendingrecord расходуетtick безcatchup.
Все3 FX/sound IDs/angles/light3 закреплены;retained audio tags могут подавлять
повторныйtag2. Guard использует IsDeath/internal flags,не произвольный server bit.
Type33 completion сбрасывает только Player-use DWORD4,не consume/item Clear.
Hover/backup сохраняютoperation;пустойcursor всё равноC1A-cancel pending aim.
Marker:slot40Draw BYTE(alpha+5),255→4;clip36 не меняетalpha;пустойshownrootпульсирует.
Firstposition доicon/fontconfigure,backgroundwidth0;mouseinput88 неfocus.
Теперь ordinary receiver lookup и geometry producer подключены,полный UI/world нет.

14chatfilters/colors/GM/category7/input/send/IME/save/legacychat и numeric
_SetSystemMsg(DWORD) открыты. en-gb/Csea.txt,en-us/Csua.txt,th-th/Csth.txt отсутствуют;
имена не подставлять. TaiwanUTF16BOM bytelexer fallback13/DBCS/signedmasks сохранены.
Full Login/secondary UI,actualTutorial,uncreatedstage failure unwind,shareddevice
lifecycle/CRT/privateABI/unsafe/null/OOM/FP/overflow/concurrency/shutdown не приняты.
Cap1024/ready guards не принимают unsafe domains. Все прежние gaps остаются;
серверы не являются blocker. Архив состояния116:research/project-memory-before117.md
и research/next-steps-before117.md. Старые детали доступны через research116 и ранее.
