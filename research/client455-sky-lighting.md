# Освещение и туман455 — участок127

**PARTIAL_COMPONENT**. Подтверждены контракты полного lighting frame и
подготовлена отдельно проверенная арифметика. Она **ещё не подключена** к
обычному игровому кадру. Текущая обычная сборка/gate остаётся126.
M6/M6F/M7/M9 открыты; полная приёмка освещения не заявлена.

Аудит: `scripts/Invoke-Python.ps1 scripts/audit_client455_sky_lighting.py`.
Отдельная проверка: `scripts/Invoke-Python.ps1 scripts/probe_client455_sky_lighting_math.py --verify-existing`.
Нативный компонент: [результат](../inventory/client455-sky-lighting-math-native.json).
Контракты/ссылки/хеши: [аудит](../inventory/client455-sky-lighting-reference.json).

## Бинарное доказательство

Обе455 x86/base400000:

- primary SHA256 `b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`;
- secondary SHA256 `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.

17 полных функций/1538 инструкций/17 диапазонов совпали между двумя455.
Проверены все страницы asm/pcode,уникальность инструкций и все положительные
CFG blockstarts. Новые полные asm:14 функций/777 инструкций. Три полных тела
8B1F20/8B1640/900B00 (761 инструкция) переиспользованы из126 без изменения.
Pcode остальных небольших getter/parameter wrappers переиспользован из126,
asm для них получен заново. Контекстные родители InitCore/R3X/script parser
не объявлены полным asm-анализом.

Raw: `artifacts/client455-progress/sky-lighting127-reference.json`,
`sky-lighting127-session.json`;native IDA session63ea5f70 saved/closed/list0.
Configured MCP smoke также прошёл,его отдельная сессия4970a219 закрыта.
Входные EXE не исполнялись;серверные файлы не менялись.

Из-за отсутствующего IDA function marker по8B1220 инструмент вернул fallback
disasm с60998total. Эта первая страница **исключена** из всех selected counts.
Getter подтверждён только точными7байтами FLD[1154DE8]/RET на обеих PE.
Он не переименован и не выдан за полный разобранный function.

## Установленный порядок кадра

После обновления часов8B1F20 при enabled:

1.900CD0 вычисляет и сохраняет позицию Sun из **предыдущих** orbit/scale;
  перевод поZ берёт из текущего far1157C88. Это не1400 из отдельного Sun draw.
2.Обновляются orbit/scale/alpha/Mie/nightweight и углы Sun.
3.8B1640 получает текущий SunColor,но смешивает его с **предыдущим** FogColor.
4.Лишь после этого вычисляет новый FogColor/Start/End по flag2 или software sky.

Нельзя менять порядок ради синхронизации:позиция и вклад старого тумана имеют
настоящую задержку на один кадр. При disabled все эти результаты сохраняются.

Sun position доступна getter8B1620 (RVA4B1620);единственный найденный прямой
consumer8CB460,его полный lens-flare pipeline пока не восстановлен.

## Два packed цвета и consumers

BF734C/BF7350 инициализированы `FFFFFFFF`. Getter8B1820 возвращает первый,
8B1830 — второй;у второго прямых xrefs в закреплённой IDB нет. Физические
названия ambient/diffuse не установлены по одним именам;в source компоненте
используются tint/direct как описания вычислений.

Tint8B1640:для RGB сначала trunc64(color×255),потом quarter contribution от
Sun и предыдущего тумана плюс128. Green сохраняет исходную последовательность
маскиFC/добавления512/shift6;каналы не заменены обычным saturating pack.
Direct color умножает RGB на alpha,потом255 с x87 trunc64 и исходными OR/shift.
Новый helper не использует clamp из отдельной отрисовки Sun.

8B30B0 (RVA4B30B0) при enabled модулирует цвет tint,сохраняет исходную alpha
и делит произведения каналов на**256**. Поэтому255×255 даёт254. При disabled
возвращает исходный цвет. Helper компонента реализует саму модуляцию,enabled
guard должен принадлежать настоящему runtime owner при интеграции.

Обычный CLevel DrawMap8E7C40 (RVA4E7C40) перед BSP задаёт
`D3DRS_TEXTUREFACTOR=GetTint()`. Такой же tint использует выбранная ветка
материала8C80A0:flag8000 и global1157CB8. Там меняются alpha/color stages.
Полный material-parent получен в pcode,но не включён в17 fullasm.
INS/Planet имеют отдельные callers,не выданы за ordinary CLevel.

## Fog endpoints и software ветка

При scene flag2:

- FogColor1157D38 — взвешенная сумма day1157D58/night1157D5C;
- FogStart1157D30 — day1157D48/night1157D4C;
- FogEnd1157D34 — day1157D50/night1157D54;
- вес — текущий night1154E08,complement1-weight остаётся в x87-регистре.

R3X first-fog flag4 заполняет текущие/day/main значения и far;second-fog flag8
заполняет night endpoints. SceneFlags берутся из offset524. InitCore обнуляет
оба endpoint набора;если night endpoints не заданы,не подставлять дневные.
Legacy commented spatial second-fog/BBMin2 код нельзя просто включить и назвать
его455 day/night interpolation. Текстовые writers также надо восстановить.

Без flag2 запускается настоящая программная ветка:

-17×17 позиций (i,j=0..16),координаты вокруг8 с шагом1290;
- высота `(4-min(sqrt((i-8)^2+(j-8)^2),4))*5160*.25`;
- для каждой позиции8B2670 рассчитывает RGB по текущим параметрам scattering
  и SunColor/intensity;это CPU-расчёт,не чтение готового GPU кадра;
- нормализует позицию,dot с direction(0,-1,0),Rayleigh/Mie coefficients,
  attenuation `pow(2,negativeLength*beta/log(2))`,phase с обратным sqrt и кубом;
  затем scattering×parameter2×SunColor×intensity,clamp0..1 и trunc×255;
- отдельные extinction/transform вычисления есть в asm,но не добавляются
  произвольно к итоговому packed RGB;полный порядок FP требует дальнейшей работы;
- суммирует каналы ненулевых packed samples,затем делит unsigned суммы на
  `trunc(count*float(exposure*.8999999761581421+.8999999761581421))`;
  результат каналов ограничивает255 и формирует opaque FogColor.

Exposure —1154DE8,setter8B1210/getter7bytes8B1220. Ordinary caller8E77B0
хранит DWORD параметр и передаёт его **младший байт/255**. Это ещё не полностью
подключённая собственная CLevel API;метод нельзя угадывать по похожему имени.
Указанные aliases/main/light/layout проверять через actual CLevel consumers.

В target нет zero-divisor fallback. Компонент возвращает точный divisor,
включая0;не подменяет divide failure успешным чёрным/дневным туманом.
Непосредственно деление с0 не исполнялось в component test.

## Новый исходный компонент и проверки

`scripts/native/client455_sky_lighting_math.h`:tint/direct pack,weighted fog
float/channel/color,colour modulation и divisor с unsigned count correction.
Сохраняет caller x87 precision/rounding;integer conversions временно выбирают
truncation и восстанавливают control word. Он пока не included ordinary engine.

`work/m9/ec0a5c6b/sky-lighting-math-001/lighting-math.jsonl`:
129cases =36Sun +45fog +24filter +24divisor. PC24/53/64 nearest-even;
independent Fraction oracle проверяет точные биты/packed DWORD. Включены
float-boundaries,weighted values вне0..1,source alpha,/256 и counts0/1/289/
high-bit unsigned;3 нулевых divisors. Все129 проходят. Это арифметические
компоненты,а не129 новых проверенных игровых функций или полный lighting frame.

Runtime126 unchanged:engine
`744733c27378f78731ce68653ca4755e8d2dcb22a53bc6b44741292a21133e55`,PE
`4dd76810b62a7137004f75e4cbd2490361a0d0180a1682e42cfa766de0626a5c`,
entry16A440. Текущие20GPU/ANI/BBX/Create1 доказательства126 остаются
историей этой же сборки;они не повторялись без изменения runtime.

## Дальше128

Подключить **всю** цепочку к ordinary CLevel:previous-position→Sun update→
old-fog tint→новый fog;вернуть оба endpoints из реального R3X/script loader,
exposure caller и TEXTUREFACTOR/CPU tint consumers. Дописать software289point
ветку с теми же коэффициентами/порядком,не использовать постоянный цвет или GPU
readback как замену. Проверить actual ordinary frame/submissions/real resources.
До runtime-изменений сохранить exact126engine/PE/MAP/rsp/reports.

Все CRT pow/cos/exp/sqrt/parity/allFP/RC/NaN/Inf,полный lens flare,
INS/Planet/general renderer/device reset/auth/stages/protocol/Character/gameplay
и client-acceptance остаются OPEN. M9 не завершён.
