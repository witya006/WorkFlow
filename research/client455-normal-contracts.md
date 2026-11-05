# Контракты модели и сброса анимации 455

2026-11-06, Asia/Yakutsk. Участок M6 номер 036. Пять методов подключены к обычной сборке
work/client455-port/normal. M6/M6F/M7/M9 остаются открытыми.

Источник — два закреплённых x86 RF_Online.bin, image base 0x400000:

- current SHA-256 b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b;
- backup SHA-256 46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.

Десять диапазонов функций и вызывающего кода совпадают между эталонами.
RVA/размеры/SHA находятся в inventory/client455-normal-contracts-reference.json.
Декомпиляция и инструкции сохранены в ignored artifacts/normal-contracts455;
для пяти методов и kernel RematchParent проверены полные страницы инструкций.
Сессия IDA b8160cd3 закрыта, сохранение подтверждено saved=true.
Входные EXE не исполнялись; серверные файлы не использовались.

| Метод | VA / RVA | Подтверждённое поведение |
|---|---|---|
| AnimationReset | 931FB0 / 531FB0 | Очистка текущих descriptors, сохранение предыдущих при включённом blending |
| RematchParent | 931A80 / 531A80 | Проверка двух моделей, вызов готового kernel 93BB70 |
| SetEyeVec | 931AC0 / 531AC0 | Первая часть с точным именем; 64 байта матрицы в +5503, флаг +5499 |
| SetTexPath | 608140 / 208140 | При непустом source strncpy255 в model+276; последний байт сохранён |
| ImportBoundBox | 931810 / 531810 | Обёртка reader93BF90: пропуск имени256, чтение второго результата перед первым |

## Существенные детали

AnimationReset не просто обнуляет кадр. У каждого меша сбрасываются byte5094,
DWORD5103 и current5095, alpha5131 становится1. Если current существует и
renderer+33840 ненулевой, прежний previous5099 освобождается, затем выделяется
descriptor32 и копируется current. Массивы ключей остаются за AnimationManager.
Сохраняются frame/max в model+684/+688, +692 становится0, +680 становится1.
В конце непустой model получает frame160/max0, даже если частей нет.
При выключенном blending или пустом current прежний previous сохраняется.
Повторный reset сам по себе не удаляет previous и не обнуляет blend elapsed.
Новые именованные поля обращаются к этим же байтам canonical1188record;
отдельных старых storage/casts нет.

RematchParent использует готовую реализацию93BB70. Перепривязываются только
меши с ненулевым external-parent5495. Поиск чувствителен к регистру, выбирает
первое совпадение; отсутствующее имя оставляет прежний parent. Проверены
вызовы из equipment451330 и actor reset7CD9F0; SetEyeVec подтверждён caller51DB70
с матрицей по значению (72 байта аргументов вместе с именем/моделью).

BBX reader открывает обычный файл rb, пропускает256 байт имени, читает12 байт
во второй output, затем12 в первый. Он не проверяет результаты fread:
открытый усечённый файл возвращает1, незаписанные байты output сохраняются.
NULL path и отсутствие файла дают0. Такое поведение сохранено явно.

## Проверка и текущий результат

- Все182 клиентских объекта, три facade CPP и20 canonical Character CPP
  собираются VS2026 x86/MT. Базовая сборка и engine033 не менялись.
- Собственный тест с двумя производственными CUnity/CAnimation модулями
  проверил пять групп: reset с выключенным/включённым blending, заменой
  previous и повтором; rematch с дубликатом/регистром/отсутствующим именем;
  полную копию eye matrix; предел/паддинг пути; настоящий GOLIATH.BBX,
  NULL/отсутствующий/усечённый файл. Реальная загрузка двух ANI также прошла.
- Реальная BN/MESH08/ANI модель прошла reset → повторное назначение ANI →
  rematch → pose → D3D9 HAL. Путь текстур установлен восстановленным методом.
  Два кадра побайтно равны сохранённому результату035; проверки обёрток,
  видимости, alpha/material и COM/Dmalloc завершения также прошли.
- MAP подтверждает поставщик всех пяти методов:
  RFClient455Facade:client455_normal_contracts.obj. Полный линк182 объектов
  теперь LNK1120:22 разных метода/данных вместо27, других ошибок нет.
  CharacterMR, заглушки и принудительное разрешение символов не использовались.

PE SHA/entry RVA/run paths, fixture/library/source hashes, MAP и кадры:
inventory/client455-normal-consumers.json, client455-normal-renderer-{math,gpu}.json,
client455-normal-link.json. Checkpoint client455-normal-contracts-checkpoint.json
имеет PARTIAL: проверенные методы не означают полноту клиента.

Повторены только затронутые consumer/renderer сценарии. Большие неизменённые
ANI/texture/shared-buffer/runtime suites не запускались.

## Открыто и следующий шаг

22 неразрешённых символа перечислены в normal-link.json: эффекты/таблицы/слоты
частиц, BeginShadow/EndShadow, accounting и _R3CalculateTime. Восстанавливать
их по455, не возвращать старую библиотеку или пустые реализации.

renderer+33840 конструктор обнуляет; нормальное включение blending и
инициализация duration33844 ещё не доказаны. Проверка включённой ветви задаёт
флаг явно. Сброс не доказывает продвижение времени перехода, весь actor lifecycle
или соответствие кадров запущенной игре455. Original OOM/unchecked AV/CRT
и профилирование также открыты; при неудачном выделении собственный adapter
выбрасывает bad_alloc. Полная игровая/UI/network приёмка — отдельная работа.

Через scripts/Invoke-Python.ps1: audit_client455_normal_contracts.py,
prepare_client455_normal.py, build_client455_normal.py,
probe_client455_normal_consumers.py, probe_client455_normal_renderer.py,
link_client455_normal.py (ожидаемый ненулевой exit1120),
checkpoint_client455_normal.py, checkpoint_client455_normal_renderer.py,
checkpoint_client455_normal_contracts.py.
