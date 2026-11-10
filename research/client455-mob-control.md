# MobControl455 и общее движение окон —163

11.11.2026. Только клиент. Gate inventory/client455-mob-control-checkpoint.json:
PARTIAL_KNOWN_FAILURE. Обычный MobControlInit вернулся после принятого сервером
выбора. Следующий отказ — старый CGUIOptionWindow при SetSprite/Init.
Игровой мир ещё не достигнут. M6/M6F/M7/M9 открыты, полных областей0/12.

## Эталоны и адреса

Primary SHA-256: b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b.
Secondary SHA-256:46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.
Оба x86/base400000. Полные страницы ASM/CFG34функций/3119инструкций сверены с
обоими pins. Raw artifacts/client455-progress/mob-control163-reference/:
mob-control.json21/2351, dependencies.json8/515, support.json5/253.

| RVA primary | Подтверждённая роль |
|---|---|
| 0x2ACFA0 / 0x2AD1E0 | Constructor / destructor |
| 0x2AD3C0 / 0x2ADA40 | Init / skins |
| 0x2ADBD0 / 0x2ADC60 | Имя / уровень |
| 0x2ADCF0 / 0x2ADDD0 | HP / FP |
| 0x2ADEB0 / 0x2AE080 | EXP / дополнительная шкала |
| 0x2AE310 / 0x2AE560 / 0x2AE5B0 | Mouse / hit bounds / open commands |
| 0x2AE720 | Update, не SetBound: прежний pointer-only кандидат уточнён |
| 0x3B4670 / 0x3B4760 / 0x3B49F0 | Регистрация движения / start / frame |
| 0x432ED0 / 0x42C5E0 | Korean / generic country name policy |

Страновой virtual53 проверен по11реальным vtables в обоих pins (22проверки
указателей). Korea: при strlen>7 отображается input+7bytes, иначе весь input.
Остальные10методов сохраняют строку. Это не приёмка всей локализации.

## Исходные владельцы

client455_mob_control_port.py подключает native/client455_mob_control.h/.inc
к обычному guimobcontrol.cpp/.h. 16дочерних controls, три кнопки команд,
clipped viewport/content; private target ABI не накладывается на legacy объект.
Натуральные summon13/1/0..1,13/0/3..4,13/2/0..4; HP/FP — main4/0/1..2,
image-text — common1/7/3 размер7×9. Старый gaugeexp не подставлен и окно не скрыто.

HP/FP принимают signed int, отрицательные current/max→0, max0→пусто, ratio
ограничен сверху1; полоса130×11, текст "%6d / %d". Уровень выводит только BYTE
число с центровкой. Имя центрируется в42pixels после странового преобразования.
EXP принимает fraction0..1: целые9pixel steps, отдельная90pixel remainder line,
float32 accumulation0.1 и cap99.989998 только для текста. Сохранены наблюдённые
округления, включая89pixel remainder при fraction1, а не идеализированные90.

Дополнительная шкала получает два signed значения. Current>=0,max>=1,
current<=max; IMUL32(100*current) оборачивается перед signed IDIV. Текст имеет
вид integerPercent% / current; нулевое значение меняет icon и скрывает шкалу,
ненулевое показывает другой icon/ступени. Target4711F0 суммирует данные из
equipped records12/13 и вызывает этот setter. Полная семантика и ordinary
inventory/equipment producer пока не перенесены; нейтральное имя SetResource455.
Первый контролируемый initial кадр до этого setter имеет шкалу в исходной позиции
0/0: он не объявлен правильным живым состоянием после игровых providers.

Mouse hover раскрывает команды; click отправляет WM_USER+0x130=0x530 с ID окна
и индексом0..2, затем закрывает. Hover/leave учитывают соседние controls.
Tooltip использует реальные language IDs3CE/3CF/39D через legacy adapter;
полные455style/owner/scheduling ещё не приняты. Legacy SetMobState оставлен
декларацией: наблюдённого caller/отдельного455body нет, поведение не выдумывается.

## Общая зависимость движения

native/client455_gui_move.inc заменяет только CGUIMoveObjectMgr в обычном
uiglobal.cpp; avatar/filter code сохраняется. Старые публичные callers остаются,
добавлены typed extended registration и явное время для воспроизводимого replay.
Продуктовые FrameMove/StartMove берут настоящий timeGetTime. В исходном screen
порядок обновления controls, затем движения сохранён.

В455 регистрация обнуляет/reuses record; timestamp0 не двигается. Duration0
сразу ставит endpoint. Обычная ветка использует точный halfPi floatDB0FC93F,
sin(double(angle)) с промежуточным округлением в float, на границе времени
ставит endpoint явно. Вторая ветка содержит скорость и ускорение; waves
возвращаются через overshoot. Удаление/освобождение записей и finished проверены.
Записи — собственные C++owners, не доступ к private памяти оригинального EXE.

## Сборка и проверки

Own SHA-256:ae592e2181809f8fd06a17a5bcbf5b7b82c6185c4160b043f4e043f8416cb89a,
x86/base400000/entryRVA1821E0/2362368bytes. VS2026:182client/67engine/20kernels,
compile/link0,unresolved0. Engine SHA4c6652a5… не менялся. Consumer proof,
own-entry/startup audit и earlyTaiwan проходят. Первый device probe корректно
остановился на guard старого early evidence; после обновления early выполнен live.

Final native work/m9/10c89a6e/mob-control-001 PASS: реальные методы/16детей,
signed HP/FP, две name policies, EXP/resource/overflow, local HWND messages для
всех3команд, clip/hit/open/close/reload. Shared movement replay проверяет
промежуточные позиции170/129, endpoints, zero duration/start, timer wrap,
overshoot/return, constant velocity и acceleration. Обычный продуктовый update
не заменялся тестовым обходом. Четыре GPUкадра initial/values/commands/reset
просмотрены, точные hashes в mob-control-visual.json. Это контролируемые поля,
не реальный summon gameplay и не сравнение с живыми кадрами оригинала455.
Native staging30assets/17904385linkedbytes/0newpoolbytes. Полного дубликата нет.

## Живая граница

work/m9/ae592e21/selection-live-taiwan001: настоящий auth/list/1/14→1/15/22/result0,
private handoff удалён. Pre-Enter PNG просмотрен: освещённый персонаж, старый
Beta0.738 UI остаётся. Полный экран выбора455 не принят.

Fatal C0000005 ownRVA12ED3F/GetSpriteXL+5F. Кандидаты стека:
988A1/CGUIObjectAni::SetSpriteInfo,9AA4A/Option.SetSprite,
9A219/Option.Init,270C9/Create_UI,26951/Create. Это candidate scan, не unwind.
Дополнительно проверены own call270C6=FF506C/return270C9 и primary Optionvtable
RVA1F0B60/slot6C→Init998A0. В обычном Create_UI MobControl.Init предшествует
Option.Init; между ними также NpcIntroduce/MoveMap/Radar/MapLoading Init.
Доказан возврат по этой последовательности, не полнота тех промежуточных окон.

## Остаток и продолжение164

Полные Animus item/board/network producers, дополнительная equipment шкала,
tooltip policy и все прежние Recall/CharInfo/Gauge gaps остаются. Не приняты
все resource reload/lifecycle/error/nonfinite/OOM/coordinate-overflow и крайние
timing/velocity domains. Проверка replay не закрывает весь игровой UI.

Следом CGUIOptionWindow: pointer-only inventory/client455-option-discovery.json,
primary vtableRVA6E4C1C, кандидаты VA7113C0/713060/714210
(RVA3113C0/313060/314210). Роли кроме предполагаемых Init/skin требуют проверки;
прежний опыт с Update6AE720 показывает, почему RTTI списка недостаточно.
Найти legacy source через rg --files, переносить owners/контракты/skins455.

Before163 сохранён135files:7193032private+3623572sharedbytes. До164 сохранить
exact163 через preserve utility --previous before163 --destination before164
--checkpoint inventory/client455-mob-control-checkpoint.json. Snapshot не менять.
IDBe410717f saved/closed/list0, native jobs завершены. Оригиналы и серверные
исходники/настройки не менялись. Учётные данные/сырые пакеты не сохранялись.

Функции2375(+28)/559(+30) из37870;22новых частичных bindings/18standalone,
всего91выборочная привязка. Общие implementation/equivalence counts не
классифицированы. Ориентир25%(20–35%)/0из12/M9OPEN сохраняется.
