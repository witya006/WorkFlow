# Окно характеристик455 в обычном клиенте —161

11.11.2026. Только клиент. Gate: inventory/client455-char-info-checkpoint.json,
PARTIAL_KNOWN_FAILURE. CharInfo прошёл обычный Init после принятого сервером
выбора персонажа; следующий отказ находится в старом CGUIRecallWindow.
Мир и полный игровой интерфейс ещё не созданы. M6/M6F/M7/M9 открыты.

## Закреплённые доказательства

Primary SHA-256: b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b.
Secondary SHA-256:46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.
Оба x86/base0x400000. Проверены все положительные CFG-диапазоны и страницы
листинга60функций/6095инструкций в обоих pins. Это объём статических материалов,
не60полностью восстановленных функций. Raw в artifacts/client455-progress/
charinfo161-reference/:charinfo.json(29/4555),values.json(26/1375),uv.json(5/165).
Адрес0x663A20 не является функцией; ошибочный дополнительный запрос остановлен
и исключён. Пагинация UV-повтора имеет обязательную проверку продвижения курсора.

Основные RVA:

| RVA | Исходный метод/роль |
|---|---|
| 0x265F70 | Outer Init → RF455CharInfoView::Init455 |
| 0x266580 / 0x266690 | Outer skins / bound |
| 0x2669A0 / 0x2667E0 | Выбор страницы / обработчик мыши |
| 0x261800 / 0x2630C0 | Main board Init / skins |
| 0x2629F0 | Названия и раскладка мастерства по расе |
| 0x263BC0 / 0x263E40 | Battle/make current+maximum, разные условия GM |
| 0x263D20 / 0x263FB0 | Ограничение прогресса, image-percent, обрезка полосы |
| 0x2640D0 | Знаковое сопротивление с minimum/maximum |

Country slots61/83 сверены по11реальным vtables и обоим pins; mapping берётся
из прежнего подтверждённого language/factory отчёта. Japan использует отступ5/
gap4, остальные10/5; Philippines/USA/Thailand выравнивают слева. Общая приёмка
всех локализаций из этого не следует. Расовая таблицаAEC350=4C5/4C6/4C7 сверена.

## Исходная реализация

scripts/client455_char_info_port.py подключает native/client455_char_info.h/.inc
к обычному guicharinfowindow.cpp после прежних преобразований Avatar/stat writers.
Владелец RF455CharInfoView содержит три настоящих TabBoard, а не private layout
оригинального C++объекта. Старые поля временно сохранены для оставшихся consumers.

Перенесены outer228x395, background/outline, header/animated highlight, close/help,
resize, wheel target и переключение трёх страниц. Реальные CharInfo ID47/common
skins; нет inventory alias или скрытия неисправного окна. Главная страница имеет
5разделов, actions2, equipment4. Последние две действительно пусты после своего
Init в эталоне; последующие наполнители/взаимодействия ещё не перенесены.

Главная страница заимствует существующие23m_uiInfoValues455:9+14строк. Добавлены
6battle/3make rows,4resist rows,7extra values, реальные language labels/colors/
раскладка. Для Accretia пропускается force row. Старые name/guild/level/HP/FP/SP/
experience writers теперь адресуют новые поля. FP/SP maximum0 дают '-',
experience использует '%.6f%%'. Реальные labels17/18 означают average defense
range/rate; старые имена методов HitRate/AvoidRate не доказывают их семантику.

Typed mastery сохраняет WORD current/maximum и разные battle/make GM условия.
Typed resist принимает signed current/min/max и обрезает полосу влево/вправо.
Старые callers не передают maximum/mastery и границы/resist: сохранённый известный
maximum и text-only resist adapter явно частичны. Произвольные лимиты не подставлены.

## Сборка и проверка

Финальный собственный BIN:
3ebd9a7dcd40b4843352f75e505a585ec65149899891f3885380040703109b08,
x86/base400000/entryRVA181DA0/2360320bytes. VS2026:182client/67engine/20kernels,
compile/link0,unresolved0. Engine SHA4c6652a5… прежний.

Final native:work/m9/db389785/char-info-001,PASS. Настоящие методы обычного окна,
три расы,23идентичных value owners,точные child counts/default раскрытия,
stroke/page/wheel,resize minimum/all viewports,GM/WORD/FP-SP0/experience,
mastery clamp/crop,signed resist и Dmalloc balance. Шесть GPUкадров.
Все шесть финальных кадров просмотрены;хеши записаны в char-info-visual.json.
Исправлены базовый button descriptor/disabled состояние и найденная затем
ошибка высоты header. В эталоне1x4/FPS5 настраивается только highlight;
header сохраняет натуральный размер common4/0. Ранние33923840/161a997c кадры
этой точной геометрии не подтверждают. Сохранён header-layout-before-fix.
Native теперь отдельно проверяет натуральную высоту/1кадр header,4кадра highlight,
позицию tabs и центр title. Сборка/native/startup/live повторены после исправления.
Staging final native:30assets/15411905linkedbytes/0newpoolbytes. Клиент не клонировался.

Первый live a51ace7e не отправил1/14: background main loop заблокировался в
GetMessage. Это НЕ подтверждение прохождения CharInfo. Его отчёт сохранён в
charinfo161-reference/attempt1-live-report.json. Драйвер теста теперь адресует
WM_ACTIVATEAPP(TRUE) только своему HWND/PID, затем спустя1.5s Enter. Это управляемая
проверка фонового обновления; OS focus/system keyboard не меняются. Продуктовый
main loop не обходился и не исправлялся этим тестовым приёмом.

Final live:work/m9/3ebd9a7d/selection-live-taiwan001. Настоящий auth/list/1/14→
1/15/22,result0. Просмотрен pre-Enter кадр:освещённый анимированный персонаж;
виден старый Beta0.738 UI,поэтому полныйselection455не принят. Handoff удалён.
После Enter один unhandledC0000005:

own12E8FF/GetSpriteXL+5F ← 982E1/CGUIObjectAni::SetSpriteInfo+61 ←
A094E/CGUIRecallWindow::SetSprite+3E ← 9FFD7/Recall::Init+337 ←
26753/CGP_MainGame::Create_UI+1A3 ← 26021/Create+41.

Caller FF506C проверен с ownRecall primary vtableRVA1F1034/slot6C→Init9FCA0.
В Create_UI CharInfo.Init предшествует Recall/SummonsSelect.Init: прежний отказ
CharInfo пройден. Это не подтверждение создания мира или полной455эквивалентности.

## Что осталось и что делать дальше

- Полные action/equipment providers,callbacks/tooltip/help-text producer.
- Mastery maximum/resist bounds и полные stat producers,семантика17/18.
- Repeated cross-race/lifecycle,reload и nonfinite/overflow/zero-range/OOM domains.
- Следующее старое окно Recall,остальной MainGameUI,карта/avatar/control/gameplay.

Только pointer navigation,не принятая реализация следующего окна:
inventory/client455-recall-discovery.json,primary vtableRVA6DFD14,
InitVA6AF7F0/SetSprite6AFC20/SetBound6AFC90. Legacy source находится в
userinterface/gamewindow/recall/guirecallwindow.cpp;title всё ещё inventory0/5,
resize7/2 и старый common namespace. Переносить реальные455контракты,не aliases.

Перед162 сохранить exact161 утилитой --previous before161 --destination before162
--checkpoint inventory/client455-char-info-checkpoint.json. Before161 уже113files:
6427189bytes private copies +4047560bytes shared prior snapshots;не перезаписывать.
Owned IDAa2513525 saved/closed,список сессий0. Серверный код/настройки и оригиналы
не изменялись. Новые навыки из обсуждения не устанавливались без запроса.

## Учёт прогресса

2310(+48) уникальных адресных функций,490(+51) полных ASM/CFG из37865.
18новых выборочных частичных source bindings;12имеют standalone symbols.
14прежних TabBoard bindings теперь находятся на подключённом ordinary owner path;
11имеют standalone symbols,остальные могут быть inline. Это переход состояния,
а не14новых target functions. Всего44выборочных bindings,не общий итог переносов.
Coarse25%(20–35%)/0из12полных областей/M9OPEN сохраняются.
