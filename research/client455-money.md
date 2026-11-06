# Avatar → inventory money — 083

2026-11-07. Client only. **PARTIAL**: this restores a dependency of Tutorial
creation, not the complete Tutorial, currency protocol or gameplay.
M6/M6F/M7/M9 remain open. Overall client completion has not been measured; the
feature registry is incomplete and closed M0–M5 are not a percentage of behavior.

## Reference evidence

Both pinned binaries are x86, image base `0x400000`:

- current SHA-256 `b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`;
- backup SHA-256 `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.

21 selected money/Tutorial body ranges match both pins. Ten money functions
have 382 actual assembly instructions, saved with pagination/count/unique-address
checks. These are not 382 instructions for all 21 selected ranges. Raw evidence:
`artifacts/client455-progress/{money083-reference,money083-assembly,tutorial083-initial,tutorial083-extra}.json`.
Their hashes, all ranges and known gaps are in
`inventory/client455-money-reference.json`. Owned IDA session `b55212f6` was
saved/closed and `idb_list` returned zero. No reference EXE ran or server changed.

| VA / RVA | Contract |
|---|---|
| `41C3D0` / `1C3D0` | Avatar Dalant setter; two words at 24120/24124, optional inventory update |
| `41C380` / `1C380` | Avatar Gold setter; two words at 24112/24116, optional inventory update |
| `42F2A0` / `2F2A0` | Avatar Dalant qword getter |
| `45FB80` / `5FB80` | Avatar Gold qword getter |
| `677990` / `277990` | Inventory Dalant setter; qword at 2160, label at 996 |
| `677A50` / `277A50` | Inventory Gold setter; qword at 2168, label at 1120 |
| `7B2780` / `3B2780` | Signed 64-bit decimal grouping |
| `7B28F0` / `3B28F0` | Double absolute-value wrapper |
| `7B2920` / `3B2920` | Double absolute-value leaf |
| `7B2AB0` / `3B2AB0` | Cleared shared 32-byte text buffer |

The separator is comma (`AA9F24` / RVA `6A9F24`). Inventory chooses the X position
of the wider currency title, choosing Gold on equal widths. It puts the amount
ten pixels before that title minus the amount's measured width; Y comes from
the corresponding currency title. Legacy fixed coordinates are not equivalent.

For negative values the formatter spills signed64 to double, takes fabs and
converts back with truncation. This exposes x87 rounding above 2^53. With masked
invalid exceptions, INT64_MIN produces the indefinite signed value and the
observed double-minus grouped output. These quirks are preserved rather than
replaced with integer abs or a conventional formatter. Unmasked exceptions,
status flags, CRT failures and foreign buffers remain outside acceptance.

## Source and targeted verification

`prepare_client455_normal.py` derives normal source copies without recoding the
legacy originals. Avatar and inventory money fields/getters/setters now use
signed64. Two inventory method bodies use the new grouped formatter and measured
title alignment. The actual Avatar setters retain the optional singleton route.
`client455_money.cpp` joins the normal facade. All 182 client objects were rebuilt
for the changed source ABI. The PE naturally retains `RF455_GetMoneyText` and the
four `_J` setter symbols; MSVC inlines FormatMoney into the retained wrapper.
No force-retain was added. The checkpoint initially looked for a standalone
FormatMoney symbol; that evidence check was corrected to the actual linked API.

The independent Python oracle supplies 23 boundary values under four rounding
modes. Full-object probes use real Avatar, inventory, GDI/D3D and localized
resources. Each locale passes 92 cases, including values above 32 bits and 2^53,
negative values and INT64 extremes. Checks cover the null inventory branch,
getter/setter propagation, text, X/Y geometry, shared buffer lifetime, control
word restoration and unchanged adjacent stage/skip fields.

Final runs are under `work/m9/5b4651a6/money-{ko-kr,ru-ru}-001`: Korea/Russia
exit zero; three GPU frames each contain 3416/3796 colored pixels respectively.
The six label crops were inspected. Full inventory Init, sprites and other
controls are not certified. Initial fixture-only corrections enabled visibility
and placed synthetic titles in a usable right column; no production behavior
was changed to conceal those fixture mistakes.

Fresh affected regressions on this same normal link:

- Account/Avatar stage and skip, MainApp Create gate, login transform, real
  send/receive/dispatch on owned packets pass. No authentication was performed.
- Actor/FX: 269 stock ticks, 12 actors/4 models, 185 draws, 148 particle draws,
  six isolated entity draws/50 pixels, nine distinct animation ticks/459 restored
  parts; warnings zero, Dmalloc 270592 before/after. Nine GPU frames/crops inspected.
  Small captures still do not establish fine reference-runtime pixel equivalence.
- Exact own WinMain reaches the real initial TCP fixture and sound; exact PE
  D3D/window/existing Create returns one. This stops before the complete game loop.

The engine is unchanged from 082: 67 objects/12 overlays, SHA-256
`9caa283a6bf8a2fa1c9a05251b6cad451296bb03bda8a1860c22a872e88fe769`.
Its unchanged startup-contract evidence is reused explicitly. Three-map and Miles
suites from 082 were **not rerun** and are not fresh 083 evidence. The unchanged
159k suites were not repeated.

Current own `RF_Online.bin`: SHA-256
`8b51618359be41530f1558a47440111196c93b441d2a597edc5b1233ffa2f6ec`,
2095104 bytes, x86, entry RVA `151490`, 182 client/20 kernel/41 facade objects,
zero unresolved symbols. WinMain is RVA `B73B0`; after-client-Create is `B751A`.
`inventory/client455-money-checkpoint.json` validates the evidence as **PARTIAL**.

## Tutorial findings and remaining work

Actual Tutorial Create (`5586D0`, RVA `1586D0`) calls common Avatar preparation
`5488F0` / `1488F0`, whose money dependencies are already 64-bit. `5588C0` is a
separate stats helper, not that Create callee. The window ID is **38**. Earlier
queue shorthand `board47` is withdrawn: **47 describes QBI selector coverage**,
not a proven board-manager slot.

No complete CGP_Tutorial owner or four-stage factory was connected in 083.
Next is its real shared UI/board/Avatar preparation, world/CAM, QBI host, follow,
local handlers/feedback, frame/input and destruction, followed by Login/game
transitions. Do not implement an ID-only switch or substitute recording hosts
for actual providers. Full inventory, legacy 32-bit/float login/network/trade/
shop/exchange money producers, complete economy/protocol, audio/FX/Character/
IME/numeric/lifecycle and all earlier client gaps remain mandatory for M9.

Reproduce the bounded unit with `Invoke-Python.ps1` and scripts
`audit_client455_money.py`, `probe_client455_money.py`,
`review_client455_money.py`, then `checkpoint_client455_money.py`.
Only use `--reviewed` after actually viewing the generated GPU sheet.
