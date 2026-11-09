# Weather owner129 — обычная карта и параметры скрипта

2026-11-10. **PARTIAL, M6**. Восстановлены три производителя packed weather,
виртуальный setter CLevel и его настоящий вызов в обычной загрузке карты.
Текущий gate: `inventory/client455-weather-owner-checkpoint.json`.
Команда: `scripts/Invoke-Python.ps1 scripts/checkpoint_client455_weather_owner.py`.
128 теперь исторический; M6/M6F/M7/M9 остаются OPEN.

## Подтверждённые контракты

Два закреплённых x86 клиента, image base0x400000:

- primary SHA-256 `b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`;
- secondary SHA-256 `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.

Шесть полных функций/1546 инструкций,7 byte ranges, все положительные CFG block starts,
полная декомпиляция выбранных функций и байты тел совпали между обоими455.
У трёх функций использованы сохранённые ранее полные assembly страницы;
происхождение и SHA-256 raw закреплены в reference report. Неизбранные
CPU/INS/Planet функции остаются исследованием, без заявления о full assembly.
Отдельно включён constructor EH tail RVA0x65E0D0/99bytes: одних contiguous
размеров шести основных функций для доказательства недостаточно.

| RVA | Подтверждённая роль |
|---|---|
| 0x4e77b0 | CLevel сохраняет DWORD по this+0x244 и передаёт lowBYTE/255 в fog exposure |
| 0x4b1210 | Запись глобального float exposure |
| 0x4ea220 | Обычная загрузка карты: material DWORD → виртуальный setter → reset → BSP |
| 0x50a4d0 | MainMaterial script, FOG/ENV и три packed weather producer |
| 0x4c42d0 | D3DCAPS9: TextureOpCaps offset144, bit21 |
| 0x4e9f40 | CLevel constructor; прямого начального присваивания weather DWORD не найдено |

Vtable VA0xB384D0 указывает на0x8E77B0. В ordinary LoadLevel VA0x8EA685
читает глобальный DWORD0x1157D3C, VA0x8EA68A получает slot15 (+0x3C),
VA0x8EA690 вызывает его. Далее VA0x8EA692 вызывает ResetTexMemSize,
VA0x8EA6A7 — BSP load. Отсутствие прямых call xrefs к setter не означает
отсутствия игрового вызова: здесь используется виртуальная таблица.

`*weather`, `*haze`, `*special_weather`: atof возвращает double, умножение
на double255, x87 trunc-to-int64 с восстановлением CW. Очищается только
целевой байт, затем OR полного DWORD/его сдвига на8/16. Ограничения0..255
и маски результата до байта нет: отрицательные и большие значения затрагивают
соседние биты. Packed DWORD имеет BSS default0 и сохраняется между загрузками;
R3X не является его producer. CLevel setter сам producer DWORD не изменяет.

**Исправление выводов126/128:** утверждение о case-sensitive FOG/ENV неверно.
VA0x90A5ED делает `_strupr` перед FOG/ENV, VA0x90ACEC делает `_strlwr`
перед weather/haze/special_weather и тремя scene flags. Возвращён исходный
uppercase вызов, late weather callback расположен после ENV. Имя файла ENV
копируется до позднего lowercase; consumed arguments не проходят новый
верхний uppercase до чтения следующего тега. Порядок отдельных if сохранён.

Глобальный0x1157CB8 — **D3DTEXOPCAPS_BUMPENVMAP**, mask0x00200000,
а не общий выключатель дневного освещения. Это подтверждают caps writer и
установленный официальный SDK `shared/d3d9caps.h`, закреплённый хешем.
Material8000 обращается к offset216 целевого материала; подменять его
legacy m_dwFlag по одному совпадению имени нельзя. Перенос этой ветки открыт.

## Исходники и сборка

Добавлены weather_parameters.h/.inc и level_weather.inc. Генерируемый
level455.h добавляет private DWORD в конец CLevel и typed virtual setter.
Все прежние member offsets сохранены; source-owned sizeof/vtable изменены.
Это не заявление о byte ABI исходной455. Поле читается после load/setter,
новое начальное значение constructor не выдумано.

Shared FI header обновлён; полная сборка182 клиентских/20 kernel модулей
прошла. Engine67/18derived,49 payload differences/10 timestamp-only/8 equal
к128; различия общих объявлений нельзя описывать как три изменённых объекта.
Engine SHA-256 `9b366d8ffab4a9cf4192b87d2f7c5dcda5ba74b278a94ccc92db0bf05e4baced`.
RF_Online.bin x86/2251264bytes/base0x400000/entryRVA0x16BAB0:
`d678c71bcfd68cd6ee6752277d2afffdfc81957a1c14a551698836df2ffca4a7`.
Unresolved0; CharacterMR и FORCE не подключены.

## Проверки и ограничения доказательств

- 90 реальных LoadMainMaterial случаев:3 packed тега ×10 входов ×PC24/53/64.
  Независимый rational oracle подтверждает full-DWORD spill и truncation;
  CW восстанавливается. Проверены mixedcase, отрицательные/выходящие за1
  значения, selected double boundaries и обычный нечисловой token→0.
- Настоящая загрузка neutralB после fixture scripts сохраняет packed0x00BF3F7F,
  записывает его в CLevel и exposure127/255. Virtual override проверен отдельным
  owner; первый DWORD сохраняется, глобальный exposure получает последнюю запись.
- Пять настоящих sky/BSP кадров, low byte0/64/128/192/255, пять fog aggregate
  сравнений с независимым oracle, по289 grid points каждый. Это1445 вычисленных
  oracle точек и5 aggregate сравнений, **не1445 поштучно захваченных native цветов**.
  Oracle использует наблюдаемый SunColor; полного CRT transcendental parity нет.
- Свежие lighting867 captured colors/3 aggregates,27 Mie cases, обе fog branches,
  script/R3X loaders и29 BSP submissions проходят. Lowercase FOG fixture исправлен.
- World76 queue/16 clock samples, fade90+27, material60 profiles/36 cases проходят.
  Всего25 GPU кадров просмотрены;20 прежних regression кадров byte-equal128.
- Точная новая PE: own-entry/imports, ANI/BBX, sound1, window/device,
  existing Create1 и startup contracts проходят. First-chance handled exceptions
  сохранены, это не доказательство полной bootstrap/game-loop приёмки.

Weather native: `work/m9/bd1e90f3/weather-owner-001`.
Lighting: `work/m9/6f38030b/sky-lighting-001`; world:`78346d12`,
fade:`43b94c91`, material:`ba00650e` — пути подробнее в native reports.
Weather warning1 — отсутствующий original trade_bel.r3e, он не заменён.
Lighting warning2 дополнительно включает намеренный bad R3X version case.

Камера neutralB в новом weather стенде направлена вверх: видны небо,
часть геометрии и тонкие полосы. Полная world/camera/material fidelity
**не принята**; причина полос ещё не установлена. Passing owner/fog tests
не закрывают эту визуальную проблему и не означают pixel parity с455.

Первый стенд упал после удаления временного CLevel: его настоящий destructor
освобождает глобальные map resources. Исправлено только время жизни второго
owner в lab — он живёт до завершения основной карты. Production destructor
не изменён. Неуспешный run сохранён отдельно, итоговым считается bd1e90f3.

Raw `weather-owner129-reference/session.json` и exact128 backups находятся
в ignored artifacts/client455-progress; tracked reports содержат их SHA-256.
Collector временно alias-ил первую assembly страницу и общий массив: duplicate
suffix проверен против семи неизменённых страниц, first page восстановлен до100
инструкций. Untrimmed raw сохранён отдельно. IDA saved/closed/list0; configured
smoke66tools прошёл. Input EXE не запускались. Originals/server не изменялись.

Следующее: реальные material8000 и CPU tint consumers, затем lensflare/localfog,
параметры и CRT/FP; INS/Planet и полная client acceptance остаются открытыми.
Старые bulk suites без нового риска не повторялись. Текущий goal turn — progress.
