# Верхняя панель состояния455 — частичная159

11.11.2026. Только клиент. Gate: inventory/client455-hud-checkpoint.json,
PARTIAL_KNOWN_FAILURE. Мир и управление пока не достигнуты.

## Идентичность и статические доказательства

Primary455 SHA-256:
b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b.
Secondary455 SHA-256:
46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.
Оба x86, база0x400000. Полный листинг/CFG11+8функций,1406инструкций,
все положительные блоки и байты подтверждены на обоих закреплённых BIN.

| Primary RVA | Подтверждённая роль |
|---|---|
| 0x269DA0 | Конструктор владельцев панели |
| 0x26A0D0 | Init:17children,3horizontal+1vertical |
| 0x26A4A0 | SetSprite:main4/common1/EtcUI49 |
| 0x26A5C0 | Выбор цвета четвёртой полосы |
| 0x26A6C0 | Unsigned clamp,отношение,геометрия,числа и CharInfo callback |
| 0x26AA20 | BYTE уровень и центрирование |
| 0x3B6110 / 0x3B5FB0 | Подготовка полос/стилей изображения чисел |
| 0x3B2B80 | Общий helper расположения |
| 0x227AE0 / 0x227E00 | Горизонтальная/вертикальная обрезка |
| 0x2633B0 / 0x263410 / 0x263470 / 0x2634E0 / 0x263550 | CharInfo значения3/9..12 |
| 0x147790 / 0x226180 / 0x226230 | Wrapper уровня/размеры кадров |

Raw: artifacts/client455-progress/hud159-reference/session.json и callbacks.json.
Проверяющий скрипт: scripts/audit_client455_hud.py.
Малый tracked реестр с хешами: inventory/client455-hud-reference.json.
RTTI discovery сам по себе не считается восстановлением поведения.

## Что перенесено

scripts/client455_hud_port.py воспроизводимо меняет только собственные копии.
scripts/native/client455_hud.inc и hud_members.inc содержат смысловые поля,
не повторяют закрытый455ABI. Уже существующий CGUIImageText455 используется
вместо несовместимого старого CGUINumber.

Background:target4/action0/frame0. Три горизонтальные полосы:frames1..3,
значки4..6. Четвёртая вертикальная полоса:frames7..9,пороги0.2f/0.7f.
Notice:target49/action0/frame1,изначально скрыт самим оригинальным Init.
Обычные числа:common1/action7/frame3,7x9;уровень:frame4,8x11.

Cur ограничен unsigned maximum; maximum0 даёт отношение1. Строка первой
тройки использует signed DWORD и формат "%8d / %d". Уровень усечён доBYTE,
центрируется в прямоугольнике22x18 от36,23. CharInfo получает отдельные
значения3/9..12,не старые случайно совпавшие индексы0.7.

Исходный descriptor хранит targetID,собственный — CSprite*. Поэтому после
UnloadTargetSprites455/SetSprite собственные указатели заново связываются.
Подмена gaugeexp.spr другой страницей и отключение панели не используются.

## Проверка на настоящих данных и обычный запуск

Own SHA-256:
afb30309dbb1c14058ef0d9a2b9b8e055ff466ef3c3f4335846a1eb5518c41ee.
x86,база0x400000,entryRVA0x17FA40,2349056bytes.
182client/67engine/20kernels,compile/link0,unresolved0. Engine прежний.

Native:work/m9/7ca856c6/hud-001,exit0. Проверены17children,геометрия,
нулевые максимумы,unsigned clamp,семь случаев цвета,подписанные числа,
уровень/CharInfo callbacks,повторная загрузка спрайтов и Dmalloc balance.
Три реальных GPUкадра просмотрены:
initial отличается от changed; changed точно совпадает с reloaded.
Это выбранная компонентная проверка,не полный игровой сценарий.
Старый bulk entry из подключённого icon-probe не выполнялся:переиспользован
только helper чтения GPUкадра. Старые большие suites не повторялись.

Ранний обычный Taiwan startup и consumer bridge проходят.
Живой запуск:work/m9/afb30309/selection-live-taiwan001.
Настоящий addressed Enter→tx1/14/1→rx1/15/22→result0. В Create_UI Gauge.Init
расположен перед CharInfo.Init;живой стек теперь дошёл до последнего.

Следующий необработанный C0000005:

| Own RVA | Символ |
|---|---|
| 0x12C53F | GetSpriteOrgXL@CSprite+0x5F |
| 0x097288 | SetSpriteInfo@CGUITileObject+0x68 |
| 0x074366 | SetSprite@CGUICharInfoWindow+0xC6 |
| 0x073301 | Init@CGUICharInfoWindow+0xB61 |
| 0x026729 | Create_UI@CGP_MainGame+0x179 |
| 0x026021 | Create@CGP_MainGame+0x41 |

Это не успешный полный запуск. Старый CharInfo ещё получает
SP_ID_INVENTORY иaction6/7;нужно восстановить target47/charinfo.spr,
реальныйlayout и его потребителей. Простое добавление файла в стенд
не докажет правильность этого окна.

## Оставшиеся ограничения

- Весь MainGame UI_LoadSprite/root,остальные окна и создание карты/Avatar/control.
- Полный нижний EXP UI,unit modes,caption/notice producers и состояния значков.
- Назначение/источники четвёртой полосы ещё не приняты:не объявлять её EXP/DP.
- Полные callbacks,hover/flags,FP/ошибочные ресурсы и lifecycle.
- Полное поведение выбора/Title/Login/мира и все12областей M9.

Функциональный ориентир25%(20–35%) не повышен. Реестр функций:
2246(+15) с адресными материалами,422(+19) с полными ASM/CFG из37865.
Новые5sourcebindings частичные;общий перенос/equivalence всё ещё не подсчитаны.
Before159 сохраняет точную158/92files. До160 сохранить текущую159.
Оригинальные установки и сервер не менялись;пароль/ключи/сырые пакеты
не сохранены,handoff удалён. Owned IDA сессии сохранены и закрыты.
