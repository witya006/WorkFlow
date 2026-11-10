# Кадр, анимация и привязанные эффекты экипировки153

10.11.2026. PARTIAL, M6/M6F/M7/M9 открыты. Только клиент.

Восстановлены отсутствовавшие тела Animation/FrameMove у собственных
CMesh/CEquip объектов. Обычные шесть default-объектов Avatar теперь имеют
производный тип CEquip, как в эталоне. Полный CPlayerProc ещё использует
старую экипировку: это необходимая зависимость его переноса, а не принятый
обычный одетый персонаж или экран выбора.

## Бинарные опоры

x86, image base0x400000. Primary SHA256
`b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`,
secondary `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.
13 полных функций,969 инструкций,137 положительных CFG-блоков: все байты
проверены на обоих закреплённых BIN. Полные регионы/RVA/хеши — в
`inventory/client455-equipment-frame-reference.json`; приватный ASM/CFG —
`artifacts/client455-progress/equipment-frame153-reference/session.json`.

- RVA0x6D190: base Animation, проверка128/mesh и обновление модели.
- RVA0x6E520: производный Animation с проверкой существования payload.
- RVA0x6D200: always update → base FrameMove → состояние и позиция event magic.
- RVA0x6DBC0: окончания анимаций видов8,9,46 и остальных; порядок условий
  последовательный, изменение анимации влияет на следующие проверки.
- RVA0x6D9B0: однократный поиск10dummy, guards mesh/0x21000/render2.
- RVA0x3E2240: позиция actor по умолчанию; имеющийся script выбирает реальную
  точку привязки, обновляет translation magic и результат; затем следует yaw.
- RVA0x6D3D0: magic создаётся у actor, WAV получает position самого equipment.
  Исправлена прежняя ошибка146, где обе операции получали actor position.

Важное уточнение: object BYTE4=2 не является проверкой ground wrapper.
Helpers RVA0x3DBE20/0x3F2C50 вызывают virtual120(kind2). CMesh vtable RVA0x6A92BC
указывает на RVA0x5040, всегда false; CEquip vtable RVA0x6A8F64 указывает на
RVA0x43C0, принимает только kind1. Поэтому оба нынешних класса не создают и
не колеблют ground magic. Для существующего always magic остаётся обновление
состояния; ground wrapper и его отдельная ветка не объявляются восстановленными.

## Что исполнено

Стенд `work/m9/55c69791/equipment-frame-001` связан с настоящими объектами
обычной сборки,Item/Resource,скелетом/моделью,ANI,magic cache и Miles WAV.

- Настоящий Avatar.SetDefaultItem создаёт производный CEquip, тип проверен
  через dynamic_cast и discriminator. Модель соединена со скелетом и настоящим
  per-part cache персонажа; приватные ABI указатели эталона не используются.
- Настоящий cloak ANI достигает конца через Animation; FrameMove переводит
  mode4 в mode3 и реально создаёт loop magic/WAV. Активная ANI не переключается.
- Реальные архивные scripts различаются:0x50006003 имеет create_type10 и
  следует за actor;0x50006004 имеет create_type17 и следует за cached Spine.
  Проверены обе позиции после движения/yaw персонажа.
- Координаты equipment(7,9,11) намеренно отличаются от actor(20,40,60).
  Miles получает именно первые. Прежний тест с совпадающими позициями не мог
  обнаружить ошибку. Проверка настоящего звука/остановки также проходит.
- Dummy поиск однократный; always effect не получает ground jitter.
  Guards кадра проверены на уже установленном контролируемом состоянии.
  Публичные Enable/Disable отдельно удаляют always effect при скрытии;
  их вызов не подменяется ожиданием, что эффект останется жив.
- Копирование обёртки сохраняет event magic/sound. Разрушение копии не
  выдумывает остановку event WAV. Пропавший magic обнуляет сохранённый ID;
  неиспользуемая pose view в этой ветке не требуется.
-21 frozen ветка конца ANI проверена на изменяемой собственной metadata
  в памяти. Для kind9/46 это контроль ветвления, не настоящие Siege visuals.
  Callback выполняет реальные FX/ANI операции; требуемый непредоставленный
  mount lift явно отказывает. Этот host не является production CPlayerProc.

Две начальные попытки стенда выявили ошибки его ожиданий: loop3 ошибочно
считался Spine17 вместо записанного в RPK create_type10; публичный Enable
удалял always effect до изолируемой проверки FrameMove. Обе причины проверены
по существующим исходным/архивным данным и исправлены. Их console сохранены
в `work/m9/7be895f4/` и `work/m9/c2c4216c/`; они не считаются PASS.
Первая попытка отчёта render не нашла baseline в snapshot; исправлена на
существующий неизменённый historical draw report, который не перезаписывался.

## Обычная сборка и сохранённое поведение

Own RF_Online.bin SHA256
`3296a413924f854a30277203c84008a02dd7732caa6b5e8c91f9e77379ffd856`,
x86,entry RVA0x17B430,2,326,016bytes.182client/67engine/20kernels,unresolved0.
Engine SHA256 остаётся
`4c6652a59c7172ad8f852d599c9a42183a5658d728ebd32959f65e1668b002b5`.
Пять новых/восстановленных virtual/frame методов удержаны обычной PE;
их собственные RVA сохранены в checkpoint. Удержание кода не означает,
что весь обычный CPlayerProc уже вызывает эти объекты.

Свежие WinMain/Create,Login и receiver трёх Avatar прошли. Login frame65,
3015ms просмотрен: всё ещё lobby/ожидание/Beta0.738, без авторизации.
First-chance профиль прежний:7×e06d7363,1×40080201,1×406d1388;
необработанных0. Никакого полного входа/выбора/мира не заявляется.

Отрисовка `work/m9/07878f1a/equipment-draw-001`: основной проход,glow,
matrix,alpha,fade и очередь прошли. Шесть полных PNG совпали с исторической150.
Текущий отдельный отчёт `inventory/client455-equipment-frame-render-native.json`.
Старый `inventory/client455-equipment-draw-native.json` оставлен как baseline.

Последняя полная storage-опись остаётся16:34:07:156.14GiB logical/42.96GiB
unique file sizes,не новый замер кластеров. Первый153staging добавил280bytes
в пул; окончательные frame/render staging — new_pool_bytes0. Собственные
EXE/maps/results новые; исходные ресурсы повторно целиком не копировались.
Удалений нет, входные EXE не исполнялись, server/originals не изменялись.

До153 exact152 сохранена:before153/manifest.json,52файла.
Текущий частичный gate:inventory/client455-equipment-frame-checkpoint.json.
Следующий ordinary edit требует snapshot154 с этим gate.

## Остаток

Главная следующая работа — настоящее владение12-slot controller в CPlayerProc,
все producers/consumers экипировки,Animation/Render/condition/UI и live providers.
Общий particle registry,ненулевые частицы,ground wrapper,undefined/unsafe
target domains,полный внешний вид/выбор/мир/игровой цикл остаются открытыми.
Результат153 не повышает грубую оценку25%(20–35%) и не закрывает полную область.
