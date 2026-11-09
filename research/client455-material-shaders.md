# Материальные шейдеры и свет частиц — участок135

2026-11-10. **PARTIAL M6**. Gate:
`inventory/client455-material-shaders-checkpoint.json`.
Реально подключены обычный BSP dispatcher,константы материала и источник света
из particle SPT. Полная приёмка455 не заявляется.

## Доказательства

Primary b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b;
secondary46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.
Архитектура x86,base400000. Новые12полных функций,2063инструкции,
13диапазонов совпали между обеими455;полные pcode/ASM/CFG,страницы<=100,
каждое положительное начало блока покрыто. SHA/RVA каждого диапазона:
`inventory/client455-material-shaders-reference.json`.

VA новых полных функций:
8B11E0 light ctor;8B2E40 list ctor;8B2E70 clear;8B2EB0 get;
8B2EE0 append;8B2FE0 position setter;8B3040 color setter;
8C7E40/8C7FA0/8C7FE0 splat stages;8E6950 particle draw;
8DB5B0 полный particle SPT loader,531строка/1529инструкций.

Полные dispatcher8C94A0 и consumer8C9230 переиспользованы из134/133 с проверкой
сырого анализа и сессий. Ничего не выводится только из имени функции.
Дополнительные partial queries показывают связи глобального списка1154E90,
inverse-view layout и per-BSP списка;они не включены в число новых full functions.
Сырые файлы `artifacts/client455-progress/material-shader135-*.json`,438584chars.
Owned IDA6540261b saved/closed/list0. Оригинальные EXE не исполнялись.

## Изменения в обычном коде

`client455_material_shader_port.py` подключает helpers к существующему
`DrawOneMatGroup(CVertexBuffer*,_BSP_MAT_GROUP*)`,который вызывает настоящий
`CBsp::RenderMatGroup`. Сохранён обычный fixed path;specialflag01000000 выбирает
registry,bind,draw,cleanup. Это не отдельный lab renderer.

Селектор shader_object — весь DWORDflag-01000001. Light_object использует
BYTE(flag>>8)-1 и BYTE(flag);обычный shader_object не сбрасывает последний light ID.
Из object читается WORD,потом getter снова индексирует objects,как в455.
Для special+splat flag01000041 реально получается objectIndex64;он не маскируется.

Матрицы projection/view/world идут вVS0/4/8 без transpose. Global1158038 — это
четвёртая строка inverse-view1158008,включая `_44`,а не отдельный XYZ+придуманный W.
Она подаётся вVS15/PS15 и,при пустом light owner,VS18.
При наличии света используются первый light.position[3]+color.r вVS18,
light.color вPS6. FOG выключается и локально не восстанавливается.

PS18.xy — signedSHORTscroll/256;z/w — поля+46/+50 первого слоя при ANY-bit
masks800001/800002. Пример:flag1 уже включаетscale,flag2 включаетspeed;
не требовать полного совпадения маски. PS17 содержит GetBumpFactor xyz и R3GetTime w.
Материальные текстуры занимают0..layerCount-1,lightmap — layerCount. Послеdraw
очищаются именно первые slots иVS/PS,lightmap остаётся.

Восстановлены splat pair stages и последний lightmap pass,включая TCI1→0,
ALPHAREF0→8,blend иcleanup. Два выбранных трёхслойных случая проверены:
ordinary fixed base и special base,каждый затем pair+lightmap. Все combinations
не сертифицированы.

## Настоящий producer света

Запись32байта:scale0=1,radius4=10,position8=0,RGB20=255. Оба токена `power`
и `radius` записывают поле+4. SPT loader читает `[light]`/`[endlight]`,публикует
последнюю запись в глобальный список и ставит particleFlag100000/mLightID1292.
Прежний отказ от этого блока удалён;остальные advanced providers остались открыты.
Уже существующий1296-byte CParticle header не расширялся.

Список имеет count и101pointer slots,включая extra slot constructor+404.
Append использует<=100,overflow уменьшает count;get проверяет толькоindex>=0.
Clear освобождает counted records и сбрасываетcount,оставляя старые pointer slots.
Выбранные valid cases проверены;overflow/ошибки не сертифицированы.

Обычный DrawCParticle при flag100000 получает запись поparticle.mLightID,
затем обновляет **destination0**,даже если выбранsource1. RGB умножается наscale
первой записи,position берётся изworld row4. Перенесён x87 FMUL/FSTP,
сохранён caller control word. Владелец живёт до глобального destructor,как target;
per-BSP light list — отдельный незавершённый owner.

## Реальные результаты

`work/m9/259e4d8e/material-shaders-001`:51реальный BSP shader draw,
layers1/2/7,семь разных actual textures,8flags,3time samples,light/fallback/retained
selector,матрицы/полная inverse-view row4,untouchedVS12/13,точные PS18 и выбранные
PS17. Два SPT загружены настоящим loader;обычный DrawCParticle переносит source1
вdestination0,потом BSP shader получает эти поля. Два splat случая/6DIP.
Warnings0. Тест поймал первоначально не включённый в generation list
renderparticle.cpp;список исправлен,повторный конечный запуск проходит.

Четыре новых controlled GPU кадра просмотрены:Fraction,light variant,Plazma,
splat. Все рисуют1111pixels реальной выбранной BSP группы. Это изолированная
геометрия,а не полный игровой кадр. Plazma ярче;выбранный splat pass затемняет
поверхности. Полная455pixel equivalence не утверждается.
Оба supplied source pairs загружаются реальным binary loader:дляPlazma на стенде
переставлены записи Init.r3o,затем исходный staging восстановлен. Оригиналы неизменны.

VS12/13 иPS16 заданы как **начальные условия стенда**. Производственный consumer
их не подменяет. В supplied Fraction/Plazma нетconsumerPS18:проверена передача
регистра,а не внешний вид новых specular эффектов.

Fresh ordinary world-frame76queue/16clock±1/5frames проходит;raw+PNG побайтно
равны просмотренному134,review переиспользован явно. Consumed world-input manifest
закреплён точной копией `artifacts/client455-progress/world-bellato-before135.json`,
поскольку fresh Bellato run обновил mutable inventory report.

Fresh full Bellato:98020vertices/85661faces/5455leaves/666groups/1187entities,
render/reload/release PASS. Dmalloc623360→11089471→11089471→623360.
Два новых кадра просмотрены. Первый равен прежнему историческому capture,
reload отличается;byte-equivalence reload не заявляется. В этом стенде время не
фиксируется;причина каждой отличающейся pixel ещё не сертифицирована.
Звук1/window/device/existingCreate1/contracts/providers проходят на новой PE.

Engine fefffffa5a03ee7fa60ddc907317182b38583901cb3ca163df35f2cd220ed8a9.
PE38c850199a27d9213094d7faa83d1d4cd7f127e0bfa2821cec576d1cc1ec9766,
2263552bytes/entry16E5B0/WinMainB9900/afterCreateB9A74/unresolved0.
67engine units,22derived;payload изменился толькоr3render/r3particle/renderparticle.
Общие заголовки неизменны,182client/20kernel повторно не компилировались.
Exact134 snapshot49files: `artifacts/client455-progress/before135/manifest.json`.
Большие неизменённые suites не повторялись. Серверы не изменены/не собирались.

## Открыто и следующий136

PS6 читает4float сoffset20 у32-byte allocation:последняя компонента за границей
объекта. Она не заменена выдуманным alpha;сертифицированы только первые3 RGB.
Полные обычные writers VS12/13/PS16,всеconsumerPS18 иunused lanes ещё нужны.

Приоритет136:полный Init.r3s fallback904B60/904590 и параметризация shader objects,
затем per-BSP light list/positive light_object routing. Positive FX/caps/failures/
OOM/overflow/malformed indices/files/real deviceReset остаются открыты.
Сохранить все прежние CRT/visibility/fog/world/stage/Login/auth/protocol/Character/
gameplay gaps из docs/client-acceptance.md. M6/M6F/M7/M9 OPEN.
