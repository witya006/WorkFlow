# 152: полная разрядность полей характеристик в обычном окне

10.11.2026. PARTIAL. Own RF_Online.bin
`579bc1666cc88309e840deb752b5cab114efde2692fcb16decb9656c915d63e6`,
x86/base400000,entry RVA179A40;182client/67engine/20kernels,unresolved0.
Gate:inventory/client455-char-info-values-checkpoint.json.

## Реальное изменение

Старые SetGenAttackFc/SetForceAttackFc/SetDeffenceFc принимали WORD:
70000 превращалось в4464. SetHitRate/SetAvoidRate были пустыми inline bodies.
Они заменены настоящими full-DWORD/float обработчиками выбранных функций455.
Source API сохраняет старые имена;это не подтверждение старой семантики metric.

RVA263370 адресует23виджета через4120+124*index.
Полные функции263850/2638B0/263910/263960/2639C0 пишут indices14..18:
два signed32диапазона,один signed32scalar,float сдвумя знаками и
целую частьfloat через lowDWORD результата __ftol2_sse.
В собственном источнике битовый DWORD не теряется до форматирования.

Настоящие обычные basic-stat rows теперь используют владельцев14/15/16.
В24выбранных обращениях окна перенесены position/style/child-registration/
selected string consumers. Это временно сохраняет старые координаты окна.
Полный455layout этим не объявляется готовым. Поля17/18 теперь получают текст,
но их полное отображение в новом расположении остаётся открытым.

## Доказательства

Шесть полных функций,185инструкций,9положительных CFG-блоков совпадают
на двух x86 pins,base400000. Полные RVA/regions/SHA находятся в
inventory/client455-char-info-values-reference.json;raw —
artifacts/client455-progress/char-info152-reference/session.json.

- primary b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b;
- secondary46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.

Native work/m9/5519fe61/char-info-values-001 проверяет настоящие
CGUICharInfoWindow/CGUIText,его Init/child containers и существующий вызов
CAvatar::UI_RefreshCharInfoWindow_WhenDismountUnit(FALSE).
70000–90000,250000–300000 и80000 доходят до своих полей без16битного усечения.
Проверены signedDWORDбитовые случаи,конечные float-форматы/усечение,
сохранение Level/Guild/class labels и фактическая регистрация трёх виджетов.
Это не записывающий callback вместо настоящего UI.

Существующий Avatar caller всё ещё использует старые metric producers.
Его прохождение **не доказывает** полный41A8B0/nonmount/mount/buff refresh455
или правильность всех числовых характеристик. Native отчёт явно оставляет
эти признаки false. GPU-отрисовка всего окна в этом стенде не выполнялась.

Первые C2065/C2248 относились к стенду:номер вкладки был private CPP define,
а метод Avatar —protected. Исправлены literal изреального define и using
в access-only derived test-class;production доступ/виртуальные тела не менялись.
Финальный exit0. Для стенда нужна только существующая mss32.dll,newpool0.

## Сохранённые ограничения

- Полные455metric getters и их реальные typed equipment/condition/mount/buff
  producers ещё не подключены. Нельзя заменить их старыми getters и объявить
  полный condition host готовым.
- Старые comparative WORD-array setters/upgrade annotations ещё не перенесены.
- Полное расположение/labels/render23полей и остальные setters остаются открытыми.
- В собственной Force/float ветке bounded storage;опасные16-byte stack-overflow
  домены эталона не приняты. Legacy NaN/Inf spelling,весь CRT/FP/locale/error
  fidelity здесь не доказаны. Проверенные форматные примеры не превышают
  определённые размеры target buffers соответствующих веток.
- Полные CPlayerProc ownership/Animation/FrameMove/Render/effects/condition/UI,
  выбор/мир/игровойцикл/M9 остаются обязательными.

Дополнительная диагностика для следующего соединения сохранена в
player-owner-diagnostics.json рядом сraw:26pcode-onlyfunctions,не полное ASM
доказательство. В частности,Avatar virtual252 ведёт через41A060 к skillboard
490EB0;463740 пишет BYTE101 и обновляет связанное info-window. GetSkill старого
board использует CSFItem cast;нельзя выдавать его за typed455payload accessor.
41C0B0/41C1B0 вычисляют показатели по настоящим предметам с fallback наdefault;
поэтому старые float-поля не заменяют эти функции.

Обычные startup/Create/Login и account/registered3Avatar прошли на итоговойPE.
Login65/3000ms просмотрен:ожидание/Beta0.738;9прежнихfirst-chance,unhandled0.
Никаких auth/selection/world результатов не заявлено.
Точная151runtime сохранена до изменений:before152/manifest.json,52файла.
IDAe3deb20c savedclosed/list0;native jobs завершены. Новых установок/удалений
нет,оригиналы/сервер не менялись,входные EXE не выполнялись. Последняя полная
опись storage остаётся16:34:07. Оценка25%(20–35%),M6/M6F/M7/M9OPEN.
