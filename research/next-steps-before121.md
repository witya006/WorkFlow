# Следующие шаги

Обновлено 2026-11-09.

120 завершён как частичный результат M6. Исправлена привязка камеры119:
обычный CLevel использует текущую view;INS — предыдущую. Проверены настоящие
световые проходы Bellato,архивный эффект и оба знака тряски от OS clock.
Актуальное доказательство: inventory/client455-world-frame-checkpoint.json.
Память и точные hashes: docs/project-memory.md;подробности:research/client455-world-frame.md.
M9 — полная приёмка клиента455 без модернизации графики;уже определён,не спрашивать.

1. Участок121:перенести реальные отличия световой геометрии.
   Regular8FE980:Attr0x10/leaf128/face5000. Magic8FEC90:Attr0x30,NormalY>0,
   width<=1000/обаBBoxконца внутриroot,face saturation2999,batch2000.
   Сначала проверить writers CBsp.worldmatrix this+372 и декларацию;старый
   source использует identity/FVF,не выдавать это за полную эквивалентность.
2. Проверить границы на малых воспроизводимых BSP fixtures и реальном Bellato.
   Сохранить target quirks;не подавлять warnings. Переиспользовать120matched
   controls,не возвращаться к metadata-only proof или большому159k прогону.
3. Затем полный ILevel/Empty/INS и frame/projection/sky/alpha/shadow/device reset,
   trajectory/quality/blur/advancedFX/independenttextureflag8.
4. Полные map UI/layer consumers;Tutorial/Avatar/Create/camera input/QBI47/IME/
   four stages/Login/auth/fullprotocol/Character и остальные client-acceptance gaps.
5. Закрыть M6/M6F только по полной матрице,затем M7 и финальная M9.

Вся работа только над клиентом;серверы читать как reference,не менять/собирать.
Входные EXE не запускать. Рабочие копии подwork/. Локальный Git безpush/publish.
Python через scripts/Invoke-Python.ps1 file.py. Subagents только по явному запросу.
Обычные native/GPU jobs последовательно. Header из normal/include подключать
через <...>,если он уже включён:копия scripts/native с #pragma once — другой путь
и может дать дубли типов. До rebuild сохранять exact engine/PE/report snapshots.
MCPdisasm<=120 instructions и проверка полноты;constructor/vtable прежде имени.
