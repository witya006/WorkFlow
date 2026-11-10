# Recall455 в обычном клиенте —162

11.11.2026. Только клиент. Gate: inventory/client455-recall-checkpoint.json,
PARTIAL_KNOWN_FAILURE. После принятого сервером выбора персонажа обычный
CGUIRecallWindow::Init вернулся. Следующий отказ — старый CGUIMobControl при
настройке числового индикатора. Мир и полный MainGame UI ещё не созданы.

## Закреплённые материалы

Primary SHA-256: b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b.
Secondary SHA-256: 46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.
Оба x86/base0x400000. Сверены полные листинги, положительные диапазоны CFG и
страницы инструкций39функций/3039инструкций в обоих pins. Raw в
artifacts/client455-progress/recall162-reference/: recall.json(31/2791),
callers.json(8/248). Это статический материал, не39готовых переносов.

| RVA первичного BIN | Роль |
|---|---|
| 0x2AE7B0 / 0x2AEE90 | Unit constructor / skin |
| 0x2AEF80 | Состояние строки |
| 0x2AF050 / 0x2AF080 / 0x2AF0E0 | Имя / уровень / предмет |
| 0x2AF140 / 0x2AF200 / 0x2AF2C0 | HP / FP / EXP |
| 0x2AF7F0 / 0x2AFC20 / 0x2AFC90 | Window Init / skin / bound |
| 0x2AFDF0 / 0x2B0020 / 0x2B0340 | Добавление / удаление / scroll |
| 0x2B0680 / 0x2B08A0 | Mouse / scroll observer |
| 0x2B08F0 / 0x2B09E0 | Отдельные settings save/restore, ещё не перенесены |

Пять wrapper-heads RVA2B0160/2B01B0/2B0220/2B0290/2B02F0 раньше не были выделены
IDA как функции. После проверки прологов и границ они определены в рабочей IDB,
сохранены полные ASM/CFG и сверены оба pins. Индекс37865→37870: это уточнение
метаданных, байты входных EXE не менялись. HexRays выдаёт positive-SP warnings;
решения по этим setters основаны на инструкциях. Нет наблюдённых xrefs —
не доказательство отсутствия вызовов.

## Исходная реализация

scripts/client455_recall_port.py подключает native/client455_recall_window.h/.inc
к обычному userinterface/gamewindow/recall/guirecallwindow.cpp. Новый исходный
владелец содержит реальные дочерние controls; это не наложение private ABI455.
Публичные legacy consumers пересобраны. Серверный код не изменялся.

Окно228×395: фон, натуральный common header, title из NDLanguage, close/help,
viewport/scrollbar и resize. Строка204×56: name/level/item, фон и три полосы,
три image-text, EXP background/underline/cover. Реальные common/summon/item/
inventory/ItemLock skins. Header не нарезается на1×4. IconType4 направляет
предмет в настоящий item atlas page24; старый тип3 не подставлен.

_recall_info40bytes: имя pointer+0, index+4, item+8, sprite+12, levelBYTE+16,
HP/maxHP+20/+24, FP/maxFP+28/+32, EXPfloat+36. Смещения проверены static_assert.
Существующий CAnimusBoard пишет именованные поля и пересобран, но весь его
игровой контракт, таблицы и сетевые производители ещё не приняты как455.

HP/FP сохраняют полные DWORD current/max, делят как unsigned, max0→0 и обрезают
полосу сверху до1. Числовой текст использует signed представление и "%8d / %d".
Натуральная ширина полос в реальном summon.spr: HP132/FP132/EXP89. EXP geometry
использует percentage/100 без верхнего clamp; только текст ограничен99.989998.
Сохранён legacy getter raw texture U, он не называется нормализованным процентом.

Состояния Enabled/Disabled/Linked/None управляют цветом cover и borrowed item.
Смена в состояние кроме Linked очищает ref; Linked сохраняет его. У оригинала
начальные index/state не инициализированы; own sentinelFFFFFFFF/-1 — явный
ограниченный выбор исходного кода, а не доказанная эквивалентность undefined state.

Добавление отвергает duplicate index, создаёт и размещает владельца строки.
Удаление сдвигает следующие строки, но намеренно не уменьшает content height:
так ведёт себя проверенный код455. Scroll/reflow, минимум высоты, mouse routes
и сообщения board/help перенесены. Полный drag/link gameplay ещё открыт.

## Сборка и компонентная проверка

Own SHA-256: e929b1ec2f57f5a86415a1ce32d7992bcf6a47efeddd7813ea1bea5b8db8f19f,
x86/base400000/entryRVA181DA0/2360320bytes. VS2026:182client/67engine/20kernels,
compile/link0,unresolved0. Engine4c6652a5… не изменился. Consumer proof, own
entry/startup audit и ранний Taiwan запуск проходят.

Final native: work/m9/a5e7bd7a/recall-001, PASS. Настоящие методы обычного окна,
восемь явно контрольных записей, duplicate rejection, DWORD HP/FP, состояния,
lookup/setters, scroll/resize, removal и сохранённая высота content, ownership.
Пять GPU-кадров empty/populated/scrolled/values/removed просмотрены; точные хеши
в recall-visual.json. Это не практическая проверка реального призыва Animus.
Staging34assets/81615873linkedbytes/0newpoolbytes; клиент не клонировался.

Первый build остановлен C++ошибкой вывода initializer_list для разных derived
типов controls; исходный список исправлен на CGUIObject* array и пересобран.
Первый native19efa851 ошибочно ожидал старую ширину140. Проверенный descriptor
имеет132/132/89; код уже использовал натуральные размеры. Исправлен тестовый
oracle, failed run не принят как доказательство. Повторён только затронутый стенд.

## Обычный живой переход и следующий отказ

Final live: work/m9/e929b1ec/selection-live-taiwan002. Настоящий auth/список/
tx1/14/1→rx8/5/9→rx1/15/22/result0. Private handoff удалён. Просмотрен точный
pre-Enter login-frame.png: персонаж освещён, остаётся старый Beta0.738 label.
Полная эквивалентность экрана выбора этим не подтверждена.

После Enter один unhandledC0000005, ownRVA12E81F/GetSpriteOrgXL+5F. Прочитанные
256DWORD дают кандидаты SetSpriteU98927, SetNumberSprite838B1,
MobControl::SetSprite94D59, MobControl::Init94659, Create_UI26D01/Create265C1.
Это скан кандидатов, не unwound call stack: среди остатков есть прежний
Recall::InitA0193. Он не трактуется как действующий caller MobControl.

Дополнительно проверены байты own caller RVA26CFE=FF506C, return26D01,
own MobControl primary vtableRVA1F066C/slot6C→Init94330 и последовательность
Recall.Init перед MobControl.Init в обычном Create_UI. Вместе с фактическим
отказом внутри MobControl это подтверждает возврат RecallInit, но не мир.

Первый live001 имел пустую диагностическую выборку стека: чтение1024bytes
пересекало границу доступной памяти. Отчёт сохранён как attempt1-live-no-stack.json.
Диагностический helper теперь читает до256DWORD по одному, до первого отказа,
и сохраняет только адреса внутри собственной PE. Сырые данные стека, аккаунта
и пакетов не сохраняются. Helper пересобран, ранний запуск/live повторены002.
Продуктовая логика не менялась ради этого наблюдения.

## Остаток и продолжение163

- Полный455Animus item/board/table/network producer и реальный summon gameplay.
- Complete cursor/link ownership; TakeOutLink остаётся legacy adapter без
  доказанного отдельного соответствия функции455.
- Custom455save/restore settings, полный UI lifecycle и повторная загрузка.
- Nonfinite/overflow/OOM и остальные непринятые координатные/ресурсные ветки.
- Следующий настоящий MobControl455, остальные окна, карта и управление.

До163 сохранить exact162: preserve utility --previous before162
--destination before163 --checkpoint inventory/client455-recall-checkpoint.json.
Before162 уже124files,7189195private+3487736sharedbytes; не перезаписывать.
Никакого полного дубликата клиента или ассетов.

Pointer-only navigation: inventory/client455-mob-control-discovery.json.
Primary vtableRVA6DFB24. Кандидаты VA6AD3C0/6ADA40/6AE720
(RVA2AD3C0/2ADA40/2AE720) на Init/skin/bound требуют полного ASM/CFG и обоих pins.
Не переносить поведение по именам, RTTI или одному decompiler output.

Owned IDAbac5c81d saved/closed, текущий idb_list0. Native jobs завершены.
Оригиналы и серверный код/настройки не изменялись.

## Учёт прогресса

2347(+37) уникальных адресных функций,529(+39) полных ASM/CFG из37870.
25новых выборочных частичных bindings,17standalone symbols; всего69выборочных
привязок, не общий итог восстановленных функций. Полные переносы/эквивалентность
всего BIN пока не классифицированы. 6.20%/1.40% — только статический охват.
Грубый ориентир25%(20–35%), полных областей0/12, M6/M6F/M7/M9OPEN сохраняются.
