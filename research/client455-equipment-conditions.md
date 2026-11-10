# Условия экипировки146: числовой компонент

PARTIAL_COMPONENT. Обычный клиент145 пока не использует этот компонент.
M6/M6F/M7/M9 остаются открыты; полные характеристики/игровые действия не приняты.

## Эталон и границы

x86/base0x400000, основной SHA-256
b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b;
второй46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.
52полные функции/2323инструкции/357положительныхCFG совпадают в обоих.
45helperfunctions собраны сейчас;семь основ4411E0/4412A0/441840/4418D0/
441970/441AC0/442460 переиспользованы из полного equipment-providers146proof.
Отдельно закреплены двеswitchтаблицы,таблица коэффициентов и виртуальные slots.

Основные RVA411E0 вход,412A0 specialmodifier,41840 обычные options,418D0
mount options,41970 upgrades,41AC0 combine,42460 weakpart;3F6E0/3F780 reset,
61F30 defence,60D10 delay,22650 upgradeview,4EA0 runtimebyte113.
Подробности:inventory/client455-equipment-conditions-reference.json.
Raw:artifacts/client455-progress/equipment-conditions146-reference/session.json.

## Исходный код

scripts/native/client455_equipment_conditions.h содержит два200-байтных блока
модификаторов,семь категорий,расчёт итогов,поиск слабой части и typed normal-item
views для живого payload и detached clone. Это собственный API,не overlay всего
приватного condition ABI. Метаданные читаются в проверенном владельце таблицы.

Воспроизведены special options,отдельные четыре option записи mount46,upgrade
modifiers,порядок armour/weapon/set/siege/flat additions и signed64 truncation lowDWORD.
Для обычных физических атак используются категории4/5/6;force использует3.
Остальные имена категорий ещё не выводятся из старого перечисления из5элементов.

Важные отличия от старого клиента:

- Коэффициенты пяти частей:0.23/0.22/0.18/0.17/0.20. Старые третий/четвёртый
  коэффициенты переставлены;исторический массив не переиспользован.
- Combine читает embedded base player processor через44C670,даже если текущий
  resource processor44C630 указывает на другой режим.
- Armour set branch использует virtual68→404EA0→payload byte113. Он не равен
  признаку upgradable изmetadata160. Это проверено на различающих входах.
- Siege multiplier применяется до flat additions и не умножает force damage.
- UI refresh вызывается до нового weakpart. При равной защите остаётся первая
  найденная часть;при отсутствии предметов weakpart=1.
- Skill-level byte читается знаково,после каждой операции дробь отбрасывается.
  Callback сохраняет старшие биты предшествующего знакового значения.
- Reset сохраняет SFblock,set selectors/values и extra708..720. Mounted
  defence456 не инициализируется этим constructor/reset и требует producer.
  Неизвестные setvalues также явно требуют настоящего producer.

## Проверка и экономия входов

Native запущен против точного полного набора объектов145,но сам путь толькоCPU.
Реальные22предмета из Item.edf:21принят и face0 корректно отклонён.
Все200байт модификаторов и итоговые значения совпадают с отдельным Python
расчётом по метаданным. Контролируемый зашифрованный fixture проверяет совмещённые
усиления,unit/profile/global ветки,byte113,порядок UI/weakpart,целочисленное
усечение и снятие через clone после удаления исходного payload.

NativePASS/exit0. Входы:настоящий Item.edf,малый fixture.edf7953байта и mss32.dll;
вsharedpool добавлено только7953байта. Не требовались GPU,модели/текстуры,шрифты
или копия всего клиента. Map сохранён возле конкретного запуска.

Owner skill/UI callbacks в стенде —recorders. Они проверяют событие и порядок,
но не являются игровой реализацией этих владельцев. Обычная PE145 не менялась.

## Следующее соединение с клиентом

1. Actual owner/profile/mount/global bonus bindings;данные/потребители SF,potion,
   upgrades/seteffects и typed CPlayerProc/Avatar/registered/frame/render.
2. Callback виртуальный252:у CPlayer tableAA8DDC→43E600 пуст;у Avatar tableAA8C54
   →41A060 вызываетboard7 и490EB0,который меняет levels реальных skill widgets.
   Диагностика сохранена вowner-bindings-diagnostic.json;этиAvatarcallees ещё
   не полное ASM-доказательство и не перенесённая игровая цепочка.
3. Global Avatar info refresh41A8B0 и оставшиеся обычные UI/appearance/selection/
   bootstrap. Общую оценку25%(20–35%) этот локальный компонент не меняет.

Не приняты undefined/unsafe/OOM/concurrent/полные FPfailure ветки и вся полнота455.
Следующий шаг —соединение обычных владельцев,не новый аудит уже закрытых52функций.
Gate:inventory/client455-equipment-conditions-checkpoint.json.
Воспроизведение черезscripts/Invoke-Python.ps1:audit_client455_equipment_conditions.py
→probe_client455_equipment_conditions.py →checkpoint_client455_equipment_conditions.py.
IDA71813681 saved/closed/list0;native завершён. Сервер/оригинальные EXE не тронуты.
