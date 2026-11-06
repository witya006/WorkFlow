# M6 lifecycle047 — завершение до создания уровня

06.11.2026. Только клиент, исходные EXE не запускались, серверы не затрагивались.
Этот участок закрывает конкретный crash до Create, не весь lifecycle 455.

## Подтверждённый контракт эталона

Закреплённые x86 PE, image base 0x400000:

- основной SHA256 `b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`;
- дополнительный `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.

IDA session dae004fd работала с work-копией IDB; закрыта с save=true.
Псевдокод и инструкции сохранены в ignored artifacts/client455-lifecycle/.
`audit_client455_lifecycle.py` проверяет девять диапазонов обоих PE и точные
байты ветвления. RVA = VA − 0x400000. Отчёт:
[client455-lifecycle-reference.json](../inventory/client455-lifecycle-reference.json).

Цепочка: ctor VA7C78E0/RVA3C78E0 → Init7C79F0/RVA3C79F0 обнуляет первый owner;
dtor7C7970/RVA3C7970 → Destroy7C82C0/RVA3C82C0 → Unload7C8F30/RVA3C8F30.
В Unload, VA7C8F3F/RVA3C8F3F, `cmp dword ptr[eax],0` проверяет сам owner.
При null код возвращает EAX=0 и не вызывает virtual release, effects cleanup
или запись глобального указателя. Это подтверждено инструкциями, не только
декомпилятором. Destroy после Unload отдельно проверяет owner перед удалением.

Create VA7C7AC0/RVA3C7AC0 выделяет8байт ILevel-derived wrapper с ctor7C7B60;
vtableAECAEC имеет release slot40→7C7CB0, пустой метод. Это не доказательство
отсутствия cleanup у других конкретных уровней и не старый большой CLevel.
В created-state Unload у эталона иной порядок эффектов, обнуление global level
и две дополнительные коллекции. Их порт остаётся открытым.

## Изменение исходников

Старый CLand::Destroy безусловно вызывает UnloadLevel. Там release-build
`assert` исчезает, и при early exit исполняется null→ReleaseLevel. Первый
font046 lab это показал: AV ownRVA7DD9C, READ null+158h, сохранённый
`work/m9/e73bb511/font-ko-kr001/exception.json` относится к тому PE, не текущему.

Генератор `prepare_client455_normal.py` теперь заменяет только assert при входе
в normal CLand::UnloadLevel подтверждённым `if(!m_pLevel)return FALSE;`.
Остальной legacy cleanup не объявлен восстановленным. Исходная база,
baseline033 и библиотека движка не менялись; байты legacy текста сохраняются.

Новая RF_Online.bin: SHA256
`11833d1e9d58d0f352a211bb92d5d84423a6f5a21fb3a721eab82f62bf9d299a`,
x86/base400000,entryRVA1485A0,1998336bytes.182client objects,20kernel,
15facade;0unresolved,без CharacterMR и /FORCE. Derived engine прежний,
SHA `d0ef3b09bf260a5d513ceb7fad6468b5dcda5cfe5ed5108eaab445e746ee2b3a`.

## Настоящий выход процессов

`probe_client455_lifecycle.py` линкует все normal client objects и текущие
библиотеки с собственным console entry. Используется настоящий глобальный
g_MainApp и его CLand. Компилятор даёт типизированный member pointer через
explicit instantiation, без угаданных offsets и изменения определения класса.

Три отдельных процесса:

1. Uncreated: до engine/Create, Unload возвращает FALSE, Destroy безопасен.
2. Engine-only: InitR3Engine/ReleaseR3Engine без создания Land.
3. Created: реальный Land.Create, legacy cleanup и повторный Destroy.

Во всех случаях настоящий CRT затем вызывает глобальные деструкторы, процесс
завершается естественно с exit0. Запись PASS перед return сама по себе не
доказательство выхода: Python отдельно проверяет фактический process exit.
Нет debugger/TerminateProcess, поддельного CLevel, подмены результатов или
пропуска деструкторов. Нативный helper SHA d0e0036d...; labs work/m9/d0e0036d.
[Отчёт](../inventory/client455-lifecycle-native.json).

Созданный legacy CLevel проверен как регрессия сохранения текущей реализации,
а не эквивалентности target ILevel/world. Full CMainApp::Create/WinMain в этих
labs не исполняются. `checkpoint_client455_lifecycle.py` оставляет PARTIAL.

Из font probe удалено предварительное Land.Create. Реальный CGUIText и
корейский/русский NDLanguage по-прежнему дают прежние кадры, независимые GDI
metrics/atlas/cache сценарии проходят, оба GUI процесса завершаются exit0.
151/179 текстовых пикселей в viewport; проблема backbuffer640×500 против
viewport480 ещё не исправлена. Это отдельные собственные GUI entry, не полный
production WinMain. [Font отчёт](../inventory/client455-font-native.json).

Точная новая fullPE отдельно прошла Korean/Russian early startup, D3D/device
ready и partial normal Create до CharData. Эти четыре startup-запуска имеют
контролируемую остановку отладчиком, их нельзя выдавать за естественный выход.
Lab font registrations очищены. Короткие ANI/BBX/model/effect/shadow/clock/
accounting сценарии прошли, прежние кадры сохранились.14scoped checkpoints
PASS/PARTIAL; большие исторические suites не повторялись.

## Оставшаяся работа

Полный typed ILevel/конкретные уровни, effects cleanup, full WinMain early-error
и full game shutdown ещё открыты. FT/ANSI/полный text API/IME/layout, launcher/
FG_CB/network/BGM и прочие M6 gaps обязательны. M6/M6F/M7/M9 не закрыты.
Следом048: _CreateCharDataMgr/global.cpp, реальные таблицы455 и дальнейший
normal Create к интерфейсу входа; неперенесённые readers не обходить.

Повтор: audit_client455_lifecycle;prepare/build normal;normal consumers/full
link;probe_client455_lifecycle;probe_client455_font;own entry/startup audit и
startup/device/Create probes;short dependent regressions;scoped checkpoints.
Все Python через scripts/Invoke-Python.ps1.
