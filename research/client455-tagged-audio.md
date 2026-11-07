# Звук с метками — зависимость ядерного прицеливания, работа103

2026-11-07. PARTIAL. Восстановлена выбранная ветка tagged3D audio: настоящий
Miles provider/listener, загрузка PCM,30 каналов на запись,64 записи кэша,
запуск и остановка по метке. Собственный CMainApp владеет сервисом, открывает
его в обычном Create и закрывает в Destroy. Сам nuclear aiming owner и его
эффект ещё не подключены; существующий отказ ядерной ветки hover сохраняется.
M6/M6F/M7/M9 OPEN. Gate: inventory/client455-tagged-audio-checkpoint.json.
Проверка: scripts/Invoke-Python.ps1 scripts/checkpoint_client455_tagged_audio.py.

## Доказательства

Оба455 x86, base400000. SHA-256:
`b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b` и
`46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.
Действующий native IDA MCP:18 полных функций/1520 инструкций/18 равных
диапазонов. RVA: Init0x4beb00, Close0x4bed40, table0x4bc680,
table release0x4bc940, ID lookup0x4bcaa0, sample loader0x4bcb90,
Collect0x4bcd60, Play0x4bd080, Stop0x4bd590, wrapper0x4bee60,
room0x4bdab0, cache hit0x4f4060, normalize0x11d5d0,
sqrt0x1db70/0x1db90, cache create0x4f37a0,
cache lookup0x4f3cf0, cache deletion0x4f3e60.
Размеры и SHA каждого диапазона находятся в reference manifest.
Raw decompilation/assembly/exploration: ignored
artifacts/client455-progress/tagged-audio103-reference.json.
Owned IDA6a70bd2b сохранена/закрыта, последующий idb_list вернул0.

Связь с прицеливанием:52AC40 вызывает wrapper8BEE60(277034,1,1),
а при отмене —8BD590(277034,1). Последний вызывает AIL_end_3D_sample
для первого канала с соответствующей меткой. Старый StopWave(DWORD)
работает с другим кэшем/2D handle и не заменяет этот контракт.
Настоящая WaveList связывает277034 с Snd/Character/Newclear/Radar_00.wav,
490026bytes. Входные WAV/DLL/M3D/ASI и их hashes записаны в manifest.

## Поведение выбранной ветки

Сервис использует свой поддерживаемый пул и порядок LRU. Это семантический
владелец, не пересадка приватных STL полей455. Выбранный wave record280
имеет30 sample handles,30 tags, shared PCM pointer, ID/kind/active и позицию.
HitCache сначала изменяет ключ и порядок LRU, затем проверяется метка.

Ненулевая метка проверяется во всех30 полях, даже у записи, переиспользуемой
для другого ID. Поэтому метка жертвы способна подавить новую загрузку:
ключ уже новый, а payload ID и звук остаются старыми. Native проверяет и
этот случай, и настоящую перезагрузку жертвы при другой метке.

Stop заканчивает первый подходящий sample, сохраняя handle и tag. Collect
освобождает завершённый handle, но при другом активном канале старая метка
остаётся и продолжает подавлять повторный запуск. Полная переработка записи
обнуляет tags. Накопитель empty в Collect инициализируется один раз на весь
проход по кэшу, как в455, а не заново для каждой записи.

Первичная загрузка устанавливает distances150/40; переиспользование старой
записи создаёт новый handle без повторного вызова этого setter. Loop1 задаёт
реальному Miles loop count0. Тридцать занятых каналов приводят к замене slot0.
Позиция — X/Z относительно listener, умноженные на0.1, Y позиции sample0.
Направление сначала нормализуется в3D, затем Y обнуляется. Нулевой вектор
делится на0 и даёт NaN; подтверждённый случай сохранён. Полная x87/FP parity
за пределами проверенных значений ещё открыта.

Порядок выбора provider: Creative Labs EAX2, затем Miles Fast2D. На этой
машине фактически открылся Miles Fast2D. Для обнаружения M3D путь поиска
нужно задать до AIL_startup. Это добавлено в обычный WinMain; Open/Close
сервиса — в CMainApp Create/Destroy. Native startup debug string подтвердил
`RF455 TaggedAudio:ready:7969:Miles Fast 2D Positional Audio` внутри точной PE.
Полный порядок startup455 ещё не принят: в target provider открывается
в звуковом Init до D3D, в нынешнем порте — в CMainApp Create после D3D.

Полная таблица даёт7969 runtime registrations; простой независимый подсчёт
строк с относительными путями даёт7932. Там встречаются комментарии/числа,
пути другого вида и прочие токены. Это разные измерения. Общая tokenizer/
alias/warning/invalid-name parity не принята на основании одного count.

## Проверка и границы

157 native проверок: настоящий CMainApp owner, real DLL/M3D/listener/PCM и
WAV радара; muted lab,30 реальных одновременно играющих каналов,64 записи
кэша и LRU; duplicate/stale/victim tags, targeted Stop, координаты, loop0,
distances150/40, закрытие и повторное открытие сервиса. Матрица cache pressure
использует собственный manifest с70 ID, ссылающимися на тот же настоящий WAV.
Это не синтетический звук и не fake sink. Громкость стенда0; запись слышимого
выхода не делалась. Native run: work/m9/a156705f/tagged-audio-001.

Первый запуск показал отсутствие providers при слишком позднем задании
redist path; порядок исправлен. Ещё один запуск выявил ошибочное предположение
стенда о числе записей >9000; оно снято. При выходе того неуспешного стенда
без штатного закрытия Miles возник AV. У стенда теперь есть RAII cleanup;
успешный итоговый запуск завершился естественно с0. Неверные исходные результаты
сохранены в отдельных ignored run directories и не считаются доказательством.

ADPCM/ASI load branches перенесены по static code, но этим WAV тестом не
приняты. Другие room/listener APIs, смешанные2D/3D consumers, failure/unsafe/
OOM/concurrency и полный shutdown требуют продолжения. Собственный Close
освобождает все3D handles; у target ReleaseWaveList kind сбрасывается внутри
цикла каналов. Точное соответствие этой странности ещё не принято.

Новая собственная PE:
`cf7ac5e0ede16f1cc382d8a15ec03f479f9c1a62cbd3fb6ce4aa39999946ccb6`,
2149888bytes/x86/base400000/entry159670/WinMainb7a60/afterCreateb7bd4,
182client/20kernels/58facade/0unresolved. Open/Close/search preparation retained
в ordinary PE; Play/Stop пока вызываются native проверкой через того же owner,
их nuclear consumer ещё не перенесён. Точная PE прошла прежний Create→1 в
офлайн launcher/TCP fixture и остановлена до game loop. Account/hotbar7/
storage3, status58 и normal consumers проходят. Шесть hover кадров просмотрены
и побайтно равны102; остальные32 GUI кадра102 и большие world/audio/159k suites
не повторялись. Engine546a7529…/67objects не менялся, baseline033 сохранён;
старый snapshot derived082 library по-прежнему отсутствует.
Original/server без изменений, входные EXE не исполнялись. Установок/remote нет.

## Далее104

В effect pipeline обнаружено ещё одно существенное расхождение: старый
_MAX_MAGIC_TRACK16, а target runtime magic record содержит64 child IDs;
target process tracks имеют шаг46 и базу60. Простой вызов старого
StartMagicEffectType не доказывает совместимость данных или эффекта455.
Нужно закрепить CProcessMagic/CMagicList layout, parser/cache/lifecycle,
восстановить настоящий cue1358041136, затем связать pending/position/frame/
cancel owner с этим эффектом, новым tagged sound и сообщениемC1A. Отказ
ядерной ветки пока сохраняется. Все прежние client acceptance gaps обязательны.
