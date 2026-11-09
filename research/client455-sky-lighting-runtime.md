# Обычный кадр освещения и тумана455 — участок128

Исторический результат128; текущий gate — weather-owner129.
Исправление129: MainMaterial делает uppercase перед FOG/ENV и lowercase
перед weather/scene flags. Старое утверждение ниже о case-sensitive tags
ошибочно. [Текущие доказательства](client455-weather-owner.md).

**PARTIAL M6**. Расчёты127 подключены к обычному CLevel::FrameMove и обоим
реальным загрузчикам материалов. Работают смешивание day/night endpoints и
программный туман по289 точкам. В DrawMapRender добавлена привязка packed tint
перед BSP. Это ещё не полное освещение или приёмка всего клиента455.

Текущий gate:
`scripts/Invoke-Python.ps1 scripts/checkpoint_client455_sky_lighting.py`.
[Результат](../inventory/client455-sky-lighting-checkpoint.json).
[Контракты127](client455-sky-lighting.md) теперь исторические;runtime126 заменён128.

## Источник поведения и границы доказательства

Использованы те же17 полных функций/1538 инструкций/17 диапазонов127 с полным
CFG покрытием. Их байты,decoded calls и literals заново проверены на обеих
455 x86/base400000:

- `b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`;
- `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.

Дополнительно целые context bodies InitCore(VA8C3400,sizeAC8),script loader
(90A4D0,size9F6),R3X loader(90AED0,size28B) совпали между двумя PE. Это
сравнение полных **байтов**,а не заявление о полном asm-анализе этих родителей.
Полный pcode и размеры из сохранённых IDA xrefs использованы для их контрактов.
Новых IDA сессий128 не открывалось;сохранённая127 сессия63ea5f70 closed/list0.

Ключевые RVA:4B1F20 lighting frame,4B2670 CPU scattering,4B1640 packed colors,
500CD0 previous-state Sun position,4E7C40 ordinary map tint bind.
Подробные хеши: [runtime-reference](../inventory/client455-sky-lighting-runtime-reference.json).
Входные EXE не исполнялись,серверные файлы не менялись.

## Подключение

Вместо отдельных clock→night→Sun вызовов FrameMove теперь делает clock→
RF455_UpdateSkyLighting. Внутри сохранён исходный порядок:

1. Позиция Sun вычисляется по предыдущим orbit/scale и текущему far.
2. Обновляются Sun/Mie/nightweight.
3. Tint использует текущий SunColor и **предыдущий FogColor**.
4. Вычисляется новый туман:flag2 endpoints либо289 CPU sky samples.

Disabled оставляет существующие результаты освещения. Позиция использует far,
а не1400 из отдельного Sun draw. Полный lens-flare consumer ещё не подключён.
GetTint/GetDirect возвращают packed значения;их физические названия
ambient/diffuse не доказаны. DrawMapRender задаёт D3DRS_TEXTUREFACTOR перед BSP.
Это не означает,что все материалы уже используют tint в своих stages.

RF455_SampleSkyColor реализует коэффициенты Rayleigh/Mie,нормализацию позиции,
phase,attenuation и итоговый scattering. Float stores и операции выполняются
через x87;коэффициенты и порядок взяты из4B2670.289 цветов суммируются и делятся
на unsigned divisor с exposure,каналы ограничиваются255. Zero-divisor fallback
не добавлен. Во всех текущих обычных тестах divisor положительный.

Mie-переход переписан с x87 elapsed spill/делением/умножением. Сохранена
исходная особенность:точное значение float19:00 boundary(.7916666865348816)
даёт day Mie0 между соседними ненулевыми значениями. Не сглаживать его.
Day Mie0/night Mie.03 здесь относятся к подтверждённому initial-parameter path;
косвенные writers всех параметров пока не восстановлены.

## Загрузчики

R3X first-fog flag4 заполняет day endpoints;flag8 — night endpoints. Отсутствующий
набор сохраняется,а не подменяется другим. InitCore обнуляет оба source-owned
набора. Общий _R3ENGINE_STATE/CLevel layout не расширялся.

Настоящий LoadMainMaterial теперь вызывает RF455_ReadSkyFogToken на месте
FOG-блоков. Legacy uppercase normalization убрана только из главного token
dispatch:у455 этот участок case-sensitive. Нижний существующий weather/env
callback сохранён в прежнем месте. Не добавлен второй общий callback в начало.

FOG_COLOR без start/end заполняет текущие/main расстояния5/5000,но **не** day
endpoint distances. FOG_COLOR2 не включает автоматически первый туман.
Заголовок R3X с другой версией отвергается до изменения endpoints.
Unchecked fscanf/fread и все неопределённые случаи коротких/повреждённых inputs
не объявлены полностью принятыми;дополнительного нового fallback нет.

## Сборка

Engine67/18derived SHA256
`df47c24a32abef705eb38b34299f0508093357f38af0add0e8b68987824b7c06`.
Payload изменён только у level/core/r3material;63 объекта byte-equal126,
0 timestamp-only. Shared headers/layouts неизменны;182 client/20kernel объекты
сохранены,ANI2/BBX smoke и обычная компоновка обновлены.

Собственный RF_Online.bin SHA256
`052f73878f4082c6cab3ad532b08ecb3ec8f250dbd0622a3db83efa5157933ce`,
2251264bytes/x86/base400000/entry16B900. WinMainB98B0/afterCreateB9A24;
unresolved0,без CharacterMR/FORCE. Fresh imports/own-entry/sound1/window/device/
contracts/existingCreate1 PASS. Обработанные first-chance40080201/E06D7363/
406D1388 сохранены,фатального сбоя нет.

Exact126 engine/PE/MAP/linkRSP и21 reports сохранены до изменений в
`artifacts/client455-progress/*before128*`;память/шаги —research/*before128.md.

## Проверки

Current native: `work/m9/a92d3696/sky-lighting-001`.
[Native report](../inventory/client455-sky-lighting-native.json).

-4 actual LoadMainMaterial cases:оба набора endpoints,FOG_COLOR-only defaults,
  case-sensitive ignored lowercase и независимые night-first значения.
-5 valid actual LoadR3X cases +1 invalid-version rejection. Проверено сохранение
  отсутствующего набора между загрузками. Затем загружена настоящая neutralB.
-27 Mie boundary cases в PC24/53/64 nearest-even совпали по битам.
-5 обычных кадров +3 дополнительных ненулевых endpoint blends,disabled preserve,
  old-fog tint packing и previous-orbit position проверены.
-3 полных17×17 сетки =867 actual CPU sample colors совпали по packed DWORD
  с независимым расчётом;все3 aggregate fog colors/divisors совпали.
  **Scattering проверен здесь в PC24.** Это не проверка всех PC/RC.
- Независимый CPU oracle использует фактические SunColor входы. Поэтому
  совпадение867 результатов **не доказывает** исходную CRT SunColor эквивалентность.
  Pow/log в software oracle тоже не являются исполняемым эталонным455.
- Exposure helper lowBYTE/255 проверен на0 и128. Его читает настоящий frame.
  Но target CLevel DWORD setter и игровые producers ещё не подключены.
-29 настоящих BSP indexed submissions с исходной neutralB camera;первый
  TEXTUREFACTOR bind обычного DrawMapRender совпал с текущим tint.

До neutralB выполнялись собственные R3X fixtures. Если сама карта не содержит
night fog,она сохраняет предыдущие значения. Это проверка сохранения состояния,
а не утверждение,что fixture значения114/6004 находятся в исходной карте.

Пять настоящих sky GPU кадров просмотрены:midnight,noon,Mie dusk,endpoint fog,
disabled. Это собственные readbacks,не сравнение с запущенным оригинальным455.
Источник камеры закреплён:
`Map/neutralB/neutralB.cam`,109548bytes,
SHA256 `4d71c20bdab6507a03904bc77c3d9cac16d062e666c923f71d7370b3030f6044`.

Регрессии:world `work/m9/c8b19052/world-frame-001`,fade
`work/m9/120a008a/sky-fade-001`,materials
`work/m9/5e4340d4/sky-material-001`. Их15 GPU кадров просмотрены и byte-equal126.
76queue/16clock/real FX+magic+regular light;90fade+27helper;
60profile/3frame/36material/unloaded PASS. Всего20 просмотренных GPU кадров128.
Wide159k/прочие неизменные suites не повторялись. Старые16 prepass/resource
cases126 остаются историческими:код ресурсов/ветвей prepass не менялся.

Lighting warnings2 =1 deliberate invalid R3X fixture +1 отсутствующий оригинал
e_neutrala/trade_bel/trade_bel.r3e. World6 прежних R3T warning,materials1,
fade0. Отсутствующий ресурс не подменялся.

При написании native observer исправлены его LoadR3X prototype/Windows far
macro/scope ошибок;production обходов не добавлено. Oracle geometry исправлен
для **отрицательного нуля Z**;успешный capture переиспользован через
--verify-existing,production геометрия не менялась.

## Что дальше129

Восстановить actual CLevel exposure DWORD owner/setter и его game callers,
material flag8000/1157CB8 stages и настоящих CPU tint consumers. Также остаются
packed weather/haze/special_weather script producers из90A4D0;их связь с
exposure подтверждать через actual callers. Наличие функций
в MAP не является доказательством этих вызовов. Затем —lens flare/local fog
volumes,indirect parameter writers,full shader/constants/CRT/FP/status flags.
Видимый software RGB восстановлен,но неиспользуемые reference transform/
extinction FP side effects пока опущены и записаны как gap.

INS/Planet,полный world/visibility/materials/device lost-reset/OOM,stages/auth/
protocol/Character/gameplay и полный client-acceptance остаются OPEN.
M6/M6F/M7/M9 не закрыты. Модернизации графики нет.
