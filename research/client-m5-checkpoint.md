# M5: первый участок455 закрыт

Исходный критерий M5 в docs/roadmap.md: восстановленный клиент загружает и использует
выбранные данные455; поведение сверено с эталоном, регрессии проходят. Выбранный
участок — helper-only SPT и его interior/weather consumer, а не весь renderer/particle.
Пределы этапа не заменяют конечную цель M9.

| Требование | Доказательство |
|---|---|
| Source loader соответствует выбранному455контракту | LoadExtDummy0x90BBF0/RVA0x50BBF0,обе pinned SHA; перенесены count reset/lowercase per record/interior4 |
| Реальные selected data загружаются | native140files/97543real records+12fixtures,2 546 931checks; сохранённый historical EXE проверяется SHA |
| Использование координат/bbox соответствует kernels455 |617instruction bytes,epsilon relocation,338own native checks в12FP modes и actual linked normal/lab checks |
| Настоящий клиентский map path | CLevel::LoadLevel/FrameMove/render/release lobby и Platform01 с RPK/model/texture на GPU |
| Actual interior consumption | Platform01:23helpers/8interiors,реальная bbox/world conversion и states двух layers[0,0]→[1,1]→[0,0] для inside/night→outside/night→outside/day |
| Regression и reproducible evidence |13GPU cases/321checks,703weather,30resource,23 337targeted helper checks; manifests/source/EXE/frame SHA,all callbacks/errors/ownership checks прошли |

Gate: scripts/verify_client_m5.py; результат inventory/client-m5-checkpoint.json.
Подробности research/client455-graphics-runtime.md и client455-resource-io-source.md.

Reference EXE не запускался. Сравнение выбранного поведения основано на pinned static
binary contracts, собственной native реализации и двух instruction-identical kernels.
Динамическая трасса всего455 не получена. GPU backend пока legacy D3D8; target455D3D9,
полные particle/clock/lighting/Character/UI/network/sound/gameplay,error/lifecycle domain
и canonical optimized build входят в M6/M6F/M7. Никакой полноты M9 здесь не заявлено.
