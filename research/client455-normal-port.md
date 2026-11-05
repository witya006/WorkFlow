# Обычный клиент: типы 455 и менеджеры

2026-11-05, участок M6 номер 034. M6/M6F/M7/M9 открыты. Рабочая копия
work/client455-port/normal; база work/client-build и engine033 сохранены.
Серверные файлы не использовались и не менялись.

Все 180 исходных клиентских единиц компилируются с D3D9 и типами 455. CUnity
выделен из global.cpp, CAnimation — из cresobject.cpp в производственные TU.
Тела методов сохранены побайтно и удалены из прежних файлов: каждый метод
компилируется один раз. Итого 182 объекта x86/MT и RFClient455Facade.lib.
Границы выделения и реальные тела проверяет checkpoint; отдельные примеры
проверяют комментарии/строки, вложенность, отсутствие маркера и обрыв тела.

CharacterMR не используется. Неизвестные методы/данные остаются link errors.
Полная линковка всех 182 объектов: LNK1120, 39 различных недостающих символов,
без других ошибок. Это не прежние 39 функций SDK; состав отличается.
Перечень с потребителями — inventory/client455-normal-link.json.
Нормальной RF_Online.bin в этой новой ветви пока нет.

В копиях трёх заголовков добавлены именованные представления подтверждённых
455 байтов. Размеры 1188/5803/284; старые 776/1072/280 не приводятся к новым.
Коллекции и исходные ядра используют те же RF455 storage, без shadow объектов.
Wrappers C++ — собственный API, не утверждение о полном original ABI.

| Тип | Важные смещения |
|---|---|
| Модель 1188 | load264, parent272, count532, mesh536, frame672, max676, ramp704/708/712/716, material720, alpha792 |
| Меш 5803 | parentFlag512, parent518, bones522, palette646, final4830, previous4894, local4958, alpha5131 |
| Анимация 284 | load0, attempted4, name5, ID264, raw268, descriptors272, max276, extra280 |

Основание — готовые проверенные Character/animation/pose/draw ядра. Бинарные
SHA/RVA/x86 находятся в их reference отчётах. Нового анализа/сессий IDA нет.
sizeof/offsetof и доступ через именованные поля/байты проверены. Anonymous unions
и packed matrices используют MSVC x86. Конструктор storage не заменяет
RF455_ConstructMeshStorage; unsafe palette/перекрытия и полный класс не приняты.
Слоты частиц/entity неизвестны: particleSlots/entitySlot не реализованы.

Проверка использует два производственных объекта. Пройдены создание/уничтожение
трёх групп CUnity, регистрация/повторный поиск, ID, дополнительные данные,
CAnimation::SetAniData/LoadData и CUnityAniMgr::GetAni. Один реальный ANI загружен
в две записи разными путями, maxFrame17920 совпал с разбором файла. Повторный
LoadData сохраняет импорт. Missing ANI оставляет load0 нулевым и attempted4
установленным; повторный вызов не сбрасывает флаг. Это не DWORD load=4.

MAP подтверждает actual GetAni/LoadData/LoadRealAnimation/RF455_LoadAnimation:
unity_managers.obj, animation_control.obj, RFClient455Facade, RFClient455Animation.
PE SHA-256/entry RVA/x86/run paths/fixture/libraries — normal-consumers.json.
Игровые DLL не загружались. Проверены два потребителя, не весь клиент/WinMain.
Hub использует pinned system d3dx9_36.dll. Его exceptions/debug logging и прочие
высокоуровневые adapters ещё не приняты как поведение 455.

Screenshot CopyRects заменён на GetRenderTargetData/SYSTEMMEM; компиляция прошла,
реальный screenshot/multisampling путь пока не проверен.

Следом: готовые pose/draw подключить через подтверждённые normal FrameMove/
DrawCharacter/SetState/UnSetState/camera/light; затем LoadMeshData/setters/reset/
bounds/effects/data из normal-link.json. Ядра повторно не восстанавливать.
Получить нормальную RF_Online.bin без CharacterMR/forced unresolved, затем
проверять normal lifecycle и игровые сценарии по client-acceptance.md.

Через Invoke-Python.ps1: prepare_client455_normal.py, build_client455_normal.py,
probe_client455_normal_consumers.py, link_client455_normal.py (сейчас ненулевой
exit ожидаем), checkpoint_client455_normal.py. Checkpoint PARTIAL не закрывает
линковку/M6/M9. Большие неизменённые наборы не запускались.
