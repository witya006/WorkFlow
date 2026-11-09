# Память проекта

Обновлено2026-11-10. **135 PARTIAL M6**,CLIENT455-MATERIAL-SHADERS-135.
Gate: inventory/client455-material-shaders-checkpoint.json.
Команда: scripts/Invoke-Python.ps1 scripts/checkpoint_client455_material_shaders.py.
Доказательства: research/client455-material-shaders.md.
Полная предыдущая память: research/project-memory-before135.md.
Предыдущий134 — progress,commit ad3f5d7. Текущий135 — progress.

## Цель и ограничения

CLIENT ONLY:поддерживаемые исходники и свойRF_Online.bin с полным поведением455.
M9 УЖЕ определён:финальная приёмка без модернизации графики. Старый Goal M9/M4
устарел. M0–M4diagnostic/selectedM5 завершены;M6/M6F/M7/M9 OPEN;M8 не нужен.
Build/Create1/selected labs не закрывают docs/client-acceptance.md.
Server только читать reference;не менять/собирать/восстанавливать,включая копии.
Originals immutable,inputEXE never execute,workcopies,localGit/no push/remote.
Subagents только явно. Python scripts/Invoke-Python.ps1 file.py,не-c/-m.
VS2026modernMSVCx86. Native/GPU sequential;timeout неrestart,опросить тот же handle.
Перед runtime edits exactengine/PE/MAP/rsp/reports/shared headers backup.
Ignored!=backup. Не повторять159k unchanged suites. Updates короткоRU<=60s.
rg--files перед неизвестными файлами. Не передавать Windows shell path globs вrg.

## Подтверждено135

Primary b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b;
secondary46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.
x86/base400000.12fullasm/2063instructions/13ranges equalboth455;fullpcode/CFG.
Новые VA:8B11E0,8B2E40,8B2E70,8B2EB0,8B2EE0,8B2FE0,8B3040,
8C7E40,8C7FA0,8C7FE0,8E6950,8DB5B0. Последний — полный particle SPT loader.
8C94A0/8C9230 полные proofs наследованы из134/133 с pinned raw/session checks.
Raw438584chars:artifacts/client455-progress/material-shader135-reference.json.
Session6540261b saved/closed/list0;живых native jobs нет.
MCP<=100asm/page AND unique/count/done/allpositiveCFG/tails. Неalias firstpage.
JSON<=20k chunks черезNode. Не угадывать имена helpers/сигнатуры/пути.

New material_shaders.inc включён перед настоящим DrawOneMatGroup,через
client455_material_shader_port.py. Настоящий CBsp::RenderMatGroup вызывает этот
путь. Special01000000:bind matrices/textures/programs/draw/cleanup. Splat40
после base draw не теряется;ordinary fixed base и special base проверены.
Shader index=wholeDWORDflag-01000001;light index=BYTE(flag>>8)-1,mode=BYTE(flag).
Ordinary shader не сбрасывает последний light selector. Special+splat01000041
даётobject64,не0. Dispatcher WORD->getter->object снова:двойная индирекция.
Binary Init.r3o count0 сохраняется;getter<=count допускаетslot0. Registry128rows.
Lightmap slot=layerCount;cleanup только0..count-1/VS/PS. Lightmap остаётся.
Raw matricesVS0proj/4view/8world,безtranspose. VS/PS15=полная inverse-view row4
1158038 (matrix1158008),включая _44. FallbackVS18 та же строка.
PS18xy signedSHORTscroll/256,z/w floats приANY mask800001/800002. PS17=bumpxyz,timew.
Fog disable не имеет local restore. VS12/13/PS16 consumer не пишет.

Shader light record32:scale0=1,radius4=10,pos8=0,RGB20=255. Power/radius пишут+4.
Particle parser [light] загружает/добавляет запись иставитflag100000/mLightID1292.
CParticle header1296 уже существовал,не расширялся. Другие advanced providers
пока отклоняются. DrawCParticle выбираетsource.mLightID,но пишет destination0;
RGB*=first.scale черезx87FMUL/FSTP,position=world row4. Global list живёт до
destructor;per-BSP список отдельный. Count+101pointers,append<=100,overflow count--,
get толькоnegativeguard,clear count0/retainslots. Overflow/OOM/malformedOPEN.
PS6fourthfloat за32-byte allocation:невыдумыватьalpha,неclaimcertification.
VS18fourthfloat=color.r лежит внутри записи. НаPS6 проверены толькоRGB3.

## Сборка и проверки

Engine fefffffa5a03ee7fa60ddc907317182b38583901cb3ca163df35f2cd220ed8a9.
PE38c850199a27d9213094d7faa83d1d4cd7f127e0bfa2821cec576d1cc1ec9766,
2263552bytes/entry16E5B0/WinMainB9900/afterCreateB9A74/unresolved0.
67engine/22derived,толькоr3render/r3particle/renderparticle payload changed.
renderparticle.cpp необходимо включать И вgeneration filenames И в1stclass list;
ранний тест обнаружил пропуск,исправлено. Shared headers unchanged,182/20 не rebuilt.
Exact134 snapshot49files:artifacts/client455-progress/before135/manifest.json.

Native work/m9/259e4d8e/material-shaders-001:51actualBSPdrawcases/layers1,2,7/
7distinctactualtextures/8flags/3times/lightfallback+producer/selectorretention/
exactPS18+selectedPS17/2SPT real loads/DrawCParticle source1->destination0/
2splatcases6DIP/wholeindex64. Warnings0. Four fresh controlled GPUframes inspected.
Fraction/light похожи,Plazma ярче,splat затемняет. Изолированная группа1111pixels,
не полный455кадр. Stock4SHO не читаютPS18:delivery proven,all specular consumers нет.
VS12/13/PS16 — явные lab initial conditions,неproduction defaults.
Plazma черезперестановку actualbinarylist;original staging восстановлен.

Fresh world-frame work/m9/0d44ffcd/world-frame-001:76queue/16clock±1/5frames
byteequal134,review reused. Consumed world-input manifest immutable alias
artifacts/client455-progress/world-bellato-before135.json (точнототжеSHA),чтобы
обновление mutable inventory Bellato не испортило provenance.
Fresh full Bellato work/m9/ecb1fd7a/world-bellato-001:98020vertices/85661faces/
5455leaves/666groups/1187entities/render+reload+release;memory623360→11089471→
11089471→623360. Два кадра просмотрены,первый byteequal старому capture,reload
отличается;byte-equivalence reload/455 не заявляется,время стенда не фиксировано.
Всего13511freshframes:6newinspected+5reviewreused. Старые остальные suites исторические.
Earlysound1/window/device/existingCreate1/contracts/providers PASS.

## Далее136/прежние инварианты

Full Init.r3s904B60/filecompiler904590,shader-object params/обычные writersVS12/13/
PS16. Затем per-BSP light list иpositive light_object route. PositiveFX/caps/
failures/OOM/overflow/invalidindices/truncation/realReset remain OPEN.
Все прежние CRT/visibility/camera/world/stages/Login/auth/protocol/Character/
gameplay acceptance gaps остаются. Не сужатьM9доselectedlabs.
133material526/7layers54/serialized46,_MAX_MATERIALS2048,typo flikering tokens.
Shared material overlay послеport_std,доparticle/vertex. Неcast332->526.
132mapauto-litflag40 producer сохранён;missingtrade_bel76 не подменять.
131lightinverse485/transform132/normalizer136 proofs сохранены;CRT nearest FSQRT/
callerPC/storecallerRC,fullmatherr/errno/unmasked/NaN/status остаются открыты.
128fog/orbitlag/oldfogtint/289grid/negativeZ/19hMie сохранены.
129uppercaseFOG/ENV/lowercaseweather,fullDWORDweather/BSS retention сохранены.
SetViewMatrix не обновляетinverse/viewproj,публиковать их явно при lab camera.
TemporaryCLevel должен жить дольше активной карты:destructor globalfree.
D3D observers patch FULLoriginalvtable57/82/83,restorebeforeforward/Get;неclone119.
M6/M6F/M7/M9 OPEN.
