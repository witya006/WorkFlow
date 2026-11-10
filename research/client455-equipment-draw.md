Актуализация150,10.11.2026: ниже сохранён отчёт149. Вывод13слотов отменён:
физически12. Guard450810 и PRNG создания/копирования теперь проверены отдельно.
Глобальная последовательность PRNG/полный lifecycle ещё не приняты. Свежий draw
regression150 и обычный Create/Login прошли;fullplayer/particles по-прежнему OPEN.
Текущая опора:research/client455-player-visual.md и player-visual-checkpoint.json.

# 149: отрисовка экипировки и очередь поз

10.11.2026. PARTIAL. Обычная собственная PE
`f4e62e487286dae42623ba28babf6f52ba527eb7604a78ce8d2a9c9b259c1c9e`,
x86/base400000/entry RVA179630,182client/67engine/20kernels,unresolved0.
Gate: inventory/client455-equipment-draw-checkpoint.json.
Полный персонаж/выбор/мир/M9 ещё не приняты.

## Исходники и подтверждённые связи

RF455EquipmentObject получил Render(default/matrix), общий выбор material/
kit/unit/item effects, alpha push/pop, optional grade overlay и RenderWithShadow.
RF455PlayerEquipmentObject вызывает ранее перенесённый AdvanceFade перед Render;
mode3 возвращает TRUE без отрисовки. Материалы148 и существующие настоящие
шейдеры/геометрия используются напрямую.

- VA450330/450710 →4506C0: перед отрисовкой slots6/7 берут BYTE metadata152,
  остальные пишут0 в поле604. Constructor/init его не инициализируют. В своей
  модели неизвестное значение явно отмечено; чтение до producer отказывает.
- VA46D8B0 →payload virtual68 →404EA0: shader/effect grade — полный BYTE113,
  не boolean. В conditions он отдельно используется как условие.
- VA46C470 делает основной проход и optional вторичную геометрию;
  VA46C940 делает Begin/End overlay без второй отрисовки. Это сохранено.
- EffectList key — DWORD. Unit kinds37..43:100*(kind−37)+metadata0.
  Декомпиляторские char-локальные не являются основанием для усечения.
- Target1072E40 загружается из Chef/Siege.ini в53F7A0; loader добавлен
  в обычный CGP_LogIn::LoadData. Собственное имя g_EFFKitList обозначает этот owner.
- VA527E70/528090/528190: максимум256, узлы>=64 ограничены63; физический
  шаг четыре матрицы/узел. Копирование BlendNum>4 перекрывает следующий узел
  и иногда следующий slot. Сохранены эти алиасы, не расширено до30/узел.
- Queue копирует source-owned resource wrapper и удерживает payload;
  Render восстанавливает позу и вызывает RenderWithShadow; Start сохраняется
  между Render, Clear обнуляет counters и освобождает владельцев.
- VA46CF10 повторяет SetMaterial/SetMeshEffect дважды и вызывает7BC8B0 со
  scale1/flag0. Перенесён этот adapter, но полный registry provider ещё открыт.

Обычная PE действительно содержит transfers:
CItemEffectRenderer::Clear→RF455_ClearEquipmentEffects455,
Render→RF455_RenderEquipmentEffects455,
RF455EquipmentObject::Render→DrawWithEffect455→CRender::DrawCharacterOverlay455.
Вторичная geometry функция теперь удержана linker. Это доказывает наличие
связей в PE, не исполнение полного player route во время Login.

## Проверка

Native: work/m9/0fdac5c0/equipment-draw-001. Настоящие Item47/catalog/model/
textures; контролируемые поза, материал и камера. Получены6 кадров:
base,overlay,matrix,alpha,fade,fade-done. Base/overlay просмотрены; совпадают
по SHA с сохранёнными прямыми backend кадрами148.

Основной проход7draws, со свечением14, matrix7. Видимая модель2659pixels,
изменение свечения2659pixels. Alpha восстановлена; fade3 не рисует,
fade-in доходит до полного состояния. Это отдельный предмет, не полный actor.

Отдельно8реальных unit/siege payloads проверены по независимому EDF fixture,
включая key>255 и numeric grade37. Queue проверена по независимому плоскому
кэшу матриц:16сравнений, в том числе пять palette entries с перекрытием
следующего узла; Start между вызовами, retain/release и предел256.
Тест предела использует resource wrapper без payload:256копий одной BYTE
reference-counted payload переполнили бы исходный счётчик. Это не объявлено
исправленным или принятым безопасным поведением455.

Две начальные попытки завершились AV в самой проверочной программе:
SetPosition(0,0,0) выбирал overload(Vector3f,BOOL,BOOL), то есть нулевой указатель.
RVA32FCD/own map установили место. Явные float-аргументы исправили fixture;
ошибочные запуски не считаются успешной проверкой production-кода.

Обычные early startup/Create/Login и затронутый account/registered receiver
с3Avatar прошли на новой PE. Login65/3016ms просмотрен: lobby/ожидание,
legacy Beta0.738. Авторизации нет.9first-chance имеют прежний профиль148,
необработанных0. Новых ресурсов в пуле финальных запусков0bytes; отдельного
полного клиента для проверки не копировали. Промежуточная реплика BBX —280bytes.

## Доказательства и незавершённое

inventory/client455-equipment-draw-reference.json объединяет уже сохранённые
27render/19backend функций148 и16новых полных функций149. Уникально62тела,
6959инструкций/650положительных CFG, проверены на двух закреплённых x86BIN.
Их SHA/RVA есть в JSON; raw под artifacts/client455-progress/equipment-*149-reference/.
Дополнительные registry pcode — только диагностика, не полное ASM-доказательство.
IDA0a6749ce сохранена/закрыта,list0. Входные EXE не выполнялись.

Перед изменениями сохранена148:before149/manifest.json. Дополнительно16точных
исходных входов148 сохранены под before149/recovered-source/: неизменённые
файлы либо обращённые изменения149, совпадение со всеми заранее записанными
SHA148 проверено. Главная runtime manifest не перезаписывалась.

Ненулевые particle/entity эффекты экипировки пока не проверены. Adapter
вызывает настоящий старый общий g_Particle, который имеет1024slots/5clones
и отличающийся failure behavior. Target7BD4A0 использует vector bounds,
шесть clones, одноразовую попытку загрузки;7BE640/7BF060 расширяют vectors
при declared count+1>3072. Нельзя переносить утверждение «2000» из RVP на
этот обычный registry без доказательства constructor. До полной приёмки
нужен его перенос; текущий adapter не считается эквивалентным всем веткам455.

Также открыты ordinary13-slot CPlayerProc/Avatar, guards/pose restore,
Animation/FrameMove/effect/conditions/UI, полный appearance/selection и
остальной client-acceptance. Constructor46BE60 потребляет rand()/100 и пишет
поле612; собственный wrapper/queue-copy этот PRNG side effect ещё не воспроизводит.
Это требуется закрыть при переносе полного lifecycle, не считать ctor принятым.
Граничные queue writes за allocation, BYTE
reference overflow, OOM/CRT/FP, device/stage/resource failure остаются gaps.
Сервер и оригиналы не менялись. Общая оценка25%(20–35%) не повышена.
