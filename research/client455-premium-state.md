# 151: настоящие владельцы Premium и бонусов Avatar

10.11.2026. PARTIAL. Обычная собственная сборка
`d1e44bb9a5b953d6fd40463f6c97250b0a72f4e235e08b91e182e7c8f7b6c7dd`,
x86/base `0x400000`, entry RVA `0x179970`;182client/67engine/20kernels,
unresolved0. Gate: `inventory/client455-premium-state-checkpoint.json`.

## Устранённая неизвестность

Ранее condition-host называл getter442440 «globalBonusEnabled», но владелец
и его producer не были установлены. Теперь подтверждено: target network-owner
constructor VA560C60 обнуляет DWORD436028 и сохраняет this в global1028AB4.
Getter RVA `0x42440` читает его, setter RVA `0x1977E0` записывает полныйDWORD.
Launcher и debug-path явно называют состояние Premium; это не признак
подключения к миру и не флаг готовности UI.

Две float-величины globalAvatar+24712/+24716 записывает RVA `0xBCB0`,
читает RVA `0xBCE0`. Их producer — handler RVA `0x1975C0` из CashShop57/12,
выбранный dispatcher RVA `0x1956C0`. Включение использует payload49/53,
отключение пишет два положительных нуля. Эти бонусы не ограничиваются снизу.

В source-owned CNetworkMgr и CAvatar добавлены реальные состояния и getters.
Обычный AnalysisServerPacket вызывает новый state-handler для57/12.
CCR launcher теперь передаёт свой уже проверенный forced-premium0 сетевому
владельцу;остальные launcher gaps сохраняются. Ничего не включает Premium
самостоятельно и не подменяет вход/авторизацию.

## Контракты и ограничения

- Status1/2:состояние1,две колонки шести семейств ставок и два combat bonus.
  Требуется57байт payload. Status0:состояние0,те же ставки и нулевые bonuses;
  эта ветка читает49байт,а не57. Status>2 игнорируется после одного байта.
- Target setter RVA `0xBB50` пишет maskFFFF и колонки0/1 шести семейств
  с порядком payload9/17/25/33/41/1. Две остальные колонки не затираются.
- Полное ASM `test AH,5 / JP` сохраняет unordered(NaN) и negativezero;
  только строго отрицательная ставка становится0. Условие `>=0` из pcode
  ошибочно нормализовало бы NaN. Реализация и независимые битовые ожидания
  следуют ASM,а не одному выводу декомпилятора.
- Неустановленные benefit cells/combat bonuses явно помечены unknown.
  Это не утверждение об обнулении неписаных полей constructor эталона.
- **Полный handler ещё не перенесён**:нет Premium window show/hide,
  icon481 и post-update Avatar virtual256 condition/UI refresh.
  Их порядок/ошибки/реентерабельность тоже не приняты. Новый entrypoint
  называется DispatchPremiumState455 и переносит только состояние.
- Полный CashShop dispatch,другие benefit writers/consumers и небезопасные
  target short-read/out-of-column domains остаются открытыми.

## Доказательства и исполнение

Полные8функций/583инструкции/64CFG-блока подтверждены на двух x86 pins,
base400000. Таблицаzero по VA `0xAA8C40` и запись global по VA `0x560E65`
также проверены. Полные RVA/regions/SHA:
`inventory/client455-premium-state-reference.json`.

- primary `b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`;
- secondary `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.

Native `work/m9/00ff6e2a/premium-state-001` вызывает настоящий обычный
AnalysisServerPacket и меняет owned состояние настоящего CAvatar.
Проверены statuses0/1/2/3/255,12ставок,сохранение остальных колонок,
DWORD getter/setter,границы57/49/1,короткие/NULL входы,NaN/-0/raw bonuses.
Никаких recording callbacks вместо целевых владельцев здесь нет.
Недостающие UI/condition callbacks явно не объявляются выполненными.
Стенду понадобилась только существующая mss32.dll;новых poolbytes0.

Ошибка первой компиляции:C2248 на protected dispatcher исправлена public
using в test-derived классе без override. Затем локальные владельцы превысили
стек проверочной программы(C00000FD);перенесены в owned heap. Это ошибки
стенда,не найденные ошибки обычного RF_Online.bin. Финальный запуск exit0.

Полная финальная сборка,затронутые consumer objects,обычные startup/Create/Login
и account/registered3Avatar прошли. Финальный Login просмотрен:
`work/m9/d1e44bb9/login-frame001/login-frame.png`,кадр65/3016мс,
ожидание/Beta0.738. Девять прежних first-chance,unhandled0.
Авторизации и полного выбора/мира нет;приёмник не присылал RF-ответов.

## Далее

Источники premium flag/bonus floats больше не неизвестны. При подключении
RF455EquipmentConditionHost использовать CNetworkMgr::PremiumState455 и
CAvatar::PremiumBenefits455().combatBonuses(),а не постоянные false/0.
Сам полный host/condition refresh и ordinary12-slot player ownership ещё
не подключены. Следующий функциональный результат остаётся правильным
персонажем в обычном клиенте,затем выбором и миром.

Точная150runtime сохранена до изменений:before151/manifest.json,53файла.
IDA dfba038a сохранена/закрыта,list0;native jobs завершены.
Новых установок/удалений нет,оригиналы/сервер не менялись,входные EXE не
выполнялись. Последний полный storage audit остаётся16:34:07;не повторялся.
Плановая оценка25%(20–35%),M6/M6F/M7/M9OPEN.
