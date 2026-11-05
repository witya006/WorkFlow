# Теневые render targets обычного клиента

2026-11-06, Asia/Yakutsk. Участок M6 номер037. BeginShadow/EndShadow подключены
к work/client455-port/normal. Полный RF_Online.bin пока не линкуется; M9 открыт.

Эталон x86/base400000, current SHA-256
b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b,
backup46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.
Пять диапазонов функций/вызывающего кода и четыре float литерала совпадают
между эталонами. RVA, размеры и SHA: inventory/client455-normal-shadow-reference.json.

| Контракт | VA / RVA |
|---|---|
| BeginShadow | 91D330 / 51D330 |
| EndShadow | 91D5C0 / 51D5C0 |
| Создание текстуры по текущему render target | 9335F0 / 5335F0 |
| Два настоящих вызывающих участка | 51DBE0 / 11DBE0; 51DE60 / 11DE60 |

Декомпиляция и инструкции сохранены в ignored artifacts/normal-shadow455.
У Begin204 инструкции: проверены120+84 строки; End41 и helper49 полные.
IDA63e04581 закрыта с saved=true. Входные EXE не исполнялись, серверы не читались.

## Реализация

client455_normal_shadow.cpp — четвёртый CPP нормального facade, без старой
CharacterMR. Текстуры лениво создаются в20 подтверждённых слотах owner+8836;
индекс>=20 возвращает0 до обращений к устройству. Размер512x512, один уровень.
Формат, usage и pool берутся из текущего render target. Helper принимает только
HRESULT==S_OK; положительный S_FALSE также даёт NULL.

Общий quad: четыре POSITION/DIFFUSE/TEX1 вершины, stride24, всего96байт.
Координаты±30, цветFFFFFFFF, UV из точных float литералов455. Process-global
массив обновляется перед первой попыткой создания VB, в том числе при её неудаче.
VB managed/usage8/FVF322; Lock(0,96,0), копирование, Unlock без проверки результата.
Если первый Lock не удался, VB остаётся: повторный Begin не заполняет его снова.
Эта особенность сохранена и воспроизведена в test-only COM capture.

Порядок Begin после подготовки: GetDepthStencilSurface → GetSurfaceLevel →
GetRenderTarget → SetRenderTarget → SetDepthStencilSurface(NULL) → Release level →
Clear target(0) → BeginScene → ZENABLE=false. Saved target/depth находятся
в последних8байтах effects, owner+8920/+8924; старые массивы не накладываются.
End ставит ZENABLE=true, вызывает EndScene, восстанавливает target/depth и
освобождает ссылки из Get. Значения освобождённых saved pointers сохраняются,
как в455; повторный End без Begin небезопасен.

Важная подтверждённая несовместимость: Begin возвращает именно HRESULT от
SetDepthStencilSurface(NULL), а не логическую1. На настоящем HAL успех даёт0.
Оба вызывающих участка455 проверяют if(result) и при0 пропускают отрисовку/End.
Успех не преобразован в1 ради работающего теста. Дальнейшие ошибки Clear/
BeginScene/SetRenderState тоже не меняют сохранённый результат. Текущий тест
явно завершает собственный проход; это не доказательство корректного обычного
игрового shadow lifecycle. Аналогично он вызывает SetState перед Begin,
чтобы Begin последним выключал Z; оригинальные BOOL callers сохранены без правок.

## Проверка

Test-only capture проверяет порядок/аргументы и сохранение Get-ссылок,
переиспользование, граничные индексы, S_FALSE от CreateTexture, неудачу CreateVB,
первый failed Lock с повтором, ignored Unlock/Clear/BeginScene/state HRESULTs
и возврат E_FAIL именно от SetDepth. Это выбранные ошибки, не все unsafe domains.

На физическом D3D9 HAL выполнены три прохода: slot0, slot19 и повтор slot0.
Проверены дескрипторы, отсутствие DS, Z=false/true, текстура/VB reuse,
возврат прежних target/depth и COM refs0 после уничтожения владельца.
Нестандартный viewport не сохраняется: после End устройство имеет полный
viewport прежнего target. Это наблюдаемое поведение реального устройства.

Реальная BN/MESH08/ANI модель прошла DrawCharacterShadow в новой текстуре.
Силуэт512x512 содержит23218 ненулевых RGB pixels; кадр просмотрен.
Отдельная очищенная текстура slot19 осталась чёрной. Два цветных кадра обычной
модели по-прежнему равны сохранённому результату035. Dmalloc/COM0, game DLLs нет.
Собственная камера и явно завершённый теневой проход не являются original-game
frame parity или приёмкой всей игровой сессии.

Все182client +4facade +20canonicalCPP собираются x86/MT. Полный линк теперь
LNK1120:20 разных методов/данных вместо22, других ошибок нет. MAP подтверждает
BeginShadow/EndShadow из RFClient455Facade:client455_normal_shadow.obj.
Большие неизменённые наборы проверок не запускались.

PE SHA/entry RVA/run paths, исходники, библиотеки, дополнительный test CPP,
MAP и normal-shadow.bgra/.bmp: inventory/client455-normal-renderer-gpu.json.
Checkpoint client455-normal-shadow-checkpoint.json имеет PARTIAL.

Открыты эффекты/таблицы/particleSlots/entitySlot, accounting и _R3CalculateTime;
ground projection91D630, GetShadow/все неактивные consumers, device reset,
полные failure/unwind и нормальный actor lifecycle ещё требуют работы.
Исходные файлы и базовая диагностическая сборка не менялись.

Через Invoke-Python.ps1: audit_client455_normal_shadow.py,
prepare_client455_normal.py, build_client455_normal.py,
probe_client455_normal_consumers.py, probe_client455_normal_renderer.py,
link_client455_normal.py (ожидаемый ненулевой exit),
checkpoint_client455_normal_shadow.py. Остальные текущие normal checkpoints
также проверены с новым составом библиотек.
