# Контейнер разделов455 и разведка окна характеристик —160

11.11.2026. Только клиент. Выполнен необходимый компонент CGUITabBoard455.
Обычный CharInfo пока остаётся старым и продолжает блокировать MainGame UI.
Gate: inventory/client455-tab-board-checkpoint.json, PARTIAL_COMPONENT_ONLY.
Это не продвижение живого клиента дальше последнего отказа159.

## Подтверждённый компонент

Primary SHA-256:
b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b.
Secondary SHA-256:
46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.
Оба x86/base0x400000. 17полных функций/1318инструкций, все положительные
CFGблоки и кодовые диапазоны совпали между pins. Raw:
artifacts/client455-progress/charinfo160-reference/tab-board.json.

| RVA | Роль |
|---|---|
| 0x220230 / 0x220360 | Конструктор/деструктор владельцев |
| 0x220410 | Init секций/контейнера/scroll observer |
| 0x220940 / 0x2209D0 | Конструктор/деструктор private group |
| 0x220A60 | Освобождение group array |
| 0x220AD0 | Изменение размеров и прокрутки |
| 0x220B60 | Два состояния заголовка |
| 0x220C00 | Надпись/цвет/центрирование |
| 0x220D40 / 0x220DB0 | Проверка/изменение раскрытия |
| 0x220FE0 / 0x2211E0 | Перестроение секций/диапазона и позиции |
| 0x221300 | Получение content container |
| 0x2213F0 / 0x221440 | Scroll observer / header mouse stroke |
| 0x220150 | Существующий getter scrollbar current amount |

Реализация: scripts/native/client455_gui_tab_board.h/.cpp.
Секции хранят собственных C++владельцев,не1268/492-byte overlays.
State раскрытия — присутствие content в child list. Сохраняются children,
геометрия,центрирование,порядок,изменение scroll range при resize.
Clear безопасно отсоединяет собственные ссылки до удаления групп.
Старое неопределённое поведение stale-list/empty reflow/allocation failure
не объявляется эквивалентным. Координатные переполнения также не приняты.

## Сборка и реальные проверки

Normal x86/VS2026:182client/67engine/20kernels,compile/link0.
Новый объект client455_gui_tab_board.obj входит в обычную facade library.
Однако в текущем RF_Online.map класс отсутствует: обычный CharInfo ещё
не вызывает его,OPT:REF удаляет код из игрового BIN. Это явно компонент.

Текущий BIN:
7354a9313c6eb43db1f267a8f575c456818021ad6284699984470285cc3c571e,
2349056bytes,entryRVA0x17FA40.
По сравнению с exact159 вbefore160 все runtime section bytes равны,
кроме двух изменившихся байт поля IMAGE_DEBUG_DIRECTORY.TimeDateStamp
RVA0x210254. Обе версии проверены: поле равно соответствующему COFFвремени
линковки. Другие различия не маскировались. Живой прогон того же поведения
не повторялся;последний реальный стек остаётся159,CharInfo.SetSprite/Init.

Native final:work/m9/a7aba19d/tab-board-001,exit0.
Пять секций с настоящими common.spr,четыре сохранённых дочерних CGUIText,
NDLanguage и реальный GPU. Проверены раскрытие/закрытие именно по stroke,
геометрия,прокрутка,clamp при увеличении viewport,повторная загрузка skins,
владение/освобождение,Dmallocbalance. Содержимое и его высоты — явно
заданные компонентные примеры,а не весь CharInfo455.
Четыре GPUкадра;расширение/scroll действительно меняют изображение.

Первое ожидание полного равенства reload-кадров оказалось неверным:
7B4E30(style0) сбрасывает thumb к6x18,а639590(total0) сохраняет его прежнюю
длину. Исследованы эти реальные функции;native проверяет обе величины,
а сравнение требует сохранения пикселей заголовков и ожидаемого изменения
ползунка. Продуктовый код не менялся ради сокрытия различия.
Итоговый Pythonstatus теперь зависит от native и всех отношений кадров.
Первый прогон с неверным ожиданием не является принятым результатом.

Shared pool final:28assets/15339609linkedbytes/0newpoolbytes.
Большие неизменённые suites не повторялись,client installation/server не менялись.

## Следующий перенос: данные только для навигации

Ниже первичная RTTI/decompiler разведка,не принятые ASM/CFG/эквивалентность:
inventory/client455-charinfo-discovery.json,
client455-charinfo-boards-discovery.json,client455-charinfo-country-discovery.json.
44decomp pages/results сохранены в
artifacts/client455-progress/charinfo160-reference/discovery-unverified.json.
Перед реализацией сверить инструкции,пагинацию и оба pins.

Outer CGUICharInfoWindow:primary vtableRVA0x6DC8DC;ctorVA665C60,
Init665F70,SetSprite666580,SetBound666690,Mouse6667E0,SelectPage6669A0.
Три embedded pages:CGUICharInfoBoard at1624,CGUICharActionBoard18548,
CGUIAuxiliaryEquipmentBoard19816. В source использовать смысловые владельцы.

Кандидаты поведения Init:228x119→bound height395;title common1/action4/frame0,
sheet1x4/FPS5;три tabicons target47/action0/frames0..2,позиции x+54/+140/+98.
Close/help:common/action0 normalframes0/3 с hover/pressed соседними.
Bottomresize common/action4/frame2;highlight common/action7/frame6,sheet1x4/FPS5.
Основная страница имеет пять expandable sections,action две,auxiliary четыре.
Member this+21180 — ready guard.

Основная страница:ctor6611F0,Init661800,SetSprite6630C0,race/layout6629F0.
23titles at1268 и23values at4120,шаг124. Первая группа9строк,вторая14.
Остальные:6battle и3make rows сprogress/image-text,4resist rows,7extra values.
Новые owners нужно связать с уже существующим m_uiInfoValues455[23].
Заголовки/NDLanguage IDs и все coordinates находятся в сохранённых страницах
661800 и tail. Не заменять их старым четырёхсекционным layout0.7.

Country candidates:slot61 только Japan возвращает1;slot83 — Philippines,
USA,Thailand. Остальные из11 возвращают0. Это влияет на интервалы и выравнивание.
Проверить соответствие factory/vtable и оба pins до принятия нового policy.
Race global _GetAvatarRace соответствует7B1CB0;language race6..8,sex15..16,
mastery-name table primaryAEC350 содержит0x4C5/0x4C6/0x4C7.
RefreshRace убирает force row дляrace/2==2. Это ещё не исходная реализация.

## Прогресс и ограничения

2262(+16) адресных функций,439(+17) полных ASM/CFG из37865.
14новых привязок к source/component,полнаяequivalencefalse;всего выборочно26.
Они не считаются14новыми функциями,работающими в обычном клиенте.
M6/M6F/M7/M9OPEN,0/12областей,ориентир25%(20–35%) прежний.
Before160:104files,7027314bytes copied/3366723shared immutable snapshot.
Owned IDA5f9b1aa3 saved/closed. До161 сохранить точный компонент160.
