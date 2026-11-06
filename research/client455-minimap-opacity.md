# Client455 minimap opacity — участок067

2026-11-06. Actual CGUIMiniMapWindow source integration of EX opacity control.
Full455minimap/world and target parent input remain OPEN. No reference EXE
executed,no server source modified.

Pins:x86/base0x400000,current SHA256
`b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`,
backup `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.
17function ranges/two vtable regions agree;10complete instruction dumps retained.
Owned IDA sessions7b53e450/b947042c saved/closed,idb_list count0. Addresses below
are RVA from base400000.

## Confirmed contracts

- `3B2C60` wraps genericalignment `3B2B80`,not a scrollbar skin helper.
  Per axis:-3far edge,-2origin,-1center,other literal coordinate. Signed32
  addition/subtraction wrap and division by2 truncates toward0.
- Actual style helper `3B5450`:common action8. Style0 background12,plain thumb
  normal13/pressed14,bottom15/16,top17/18. Style1 background6,thumb7 through
  ordinary SetSpriteInfo,top8/9,bottom10/11. Width adds arrow widths to background
  width;auto thumb disabled,horizontal style. Null scrollbar returns immediately.
  Other style bytes retain images but still execute final geometry/style changes.
- Realcommon geometry:style0 194×13,thumb10×13,arrows13×13;style1 192×15,
  thumb8×15,arrows12×15. Source does not turn style1 direct image into statearray.
- OwnerInit `3059E0`:center opacity EX against frame,move y+15,SetAmount80/80,
  assign scroll observer and add. Main frame `5:0`=400×18,grid `5:32`=400×400.
- Scrollreceiver `309E10`:for own EX,compute BYTE(signed32wrap
  `255*(current+20)/100`). Then always evaluate camera input gate,even foreign
  event source. Event ID is not used as an amount adjustment.
- Alpha `3099E0`:individual owned groups/list objects and EX preserve RGB.
  Grid background opacity is truncate(alpha×0.8) only if alpha==100(decimal),
  otherwise truncate(alpha×0.6). Final eligibility flag is alpha==100.
- Gate `1558E0`:if not suppressed return eligibility;otherwise return0,clearing
  suppression/ack only when ack is set. Cleared suppression affects next call.
  Positive branch calls `155940`,which depends on actual Avatar/world/camera
  state and is not yet restored. Source explicitly refuses that branch. Ordinary
  scrollbar amounts0..80 do not map to alpha100.
- Draw `3099A0`:container.Draw succeeds,then draw dialogs and returnTRUE.
  Confirmed helper `25EA80` iterates shown dialogs. Old0.7 map-indexFF gate and
  separately drawn outline were removed from ordinary owner Draw.

## Source integration and resource boundaries

New `client455_minimap_opacity.{h,cpp}` provides style/alignment/alpha helpers;
`client455_minimap_opacity_owner.inc` replaces/appends ordinary owner methods via
`prepare_client455_normal.py`. Owner now implements IScrollObserver and owns EX.
Existing title frame/map object become containers;title/close move into frame
hierarchy,grid into map container. Known mapped alpha groups include frame,
title,close,map,avatar,position and populated marker/tooltip lists. Other455
controls and alpha groups are still absent. Legacy object/tooltip containers
were not assigned alpha without a confirmed corresponding target operation.

The0.7 global sprite enum has ID4=inventory,but455 ID4=main. Main image uses an
owned CSprite loaded from the confirmed455path,with explicit release in owner
destructor. Global ID4 is not overwritten while other legacy consumers remain.
This is an owned compatibility bridge,not target private resource-manager ABI.
Korea reads fallbackCommon/main.spr DXT1;Russia localizedmain.spr ARGB21. Original
fallback paths are preserved in labs. Main/common inputs are SHA-pinned.

The grid on screenshots is the main5:32 image,**not loaded terrain**. Dynamic map
sprite56 and its producer are missing. At partial alpha,the inherited0.7
CGUIObject nullsprite rectangle fallback visibly fills the map area gray. This
is an explicit render gap,not evidence of455map equivalence. Full layout,
markers/tooltips/data generation,additional controls and lifecycle are open.

## Verification

Own probe links actual ordinary client objects,uses real CMainApp.LoadData,
CMouseDev.Update,owner.InputProc,EX handlers and CGUIObject event queue. No direct
observer shortcut is used for mouse tests. Fixture buttons are muted so these
tests do not claim audio behavior. First pressed-state fixture expected PRESSED
alone;corrected to HOVERED|PRESSED as ordinary input emits,without changing
production button state rules.

Checks cover81queued amount values,RGB preservation and populated lists,
alpha100 background/gate/ack,foreign event behavior and explicit camera refusal,
style0/1 resource geometry and generic alignment including negative odd sizes.
Actual input exercises:

| Action | Result |
|---|---|
| Left arrow from80 | amount79,alpha252 |
| Track click | amount17,alpha94 |
| Drag to visible endpoint | amount78,alpha249;inherited snap track162 versus visible158 |
| Release at same pointer | amount78,thumb realigns to own track offset154 |

Own probe SHA256
`c8d0f03ba214073f0d7f0e77972b5d4796b0dd983dbaff307f8aa7070e09f96e`,
x86/entryE4380,Ko/Ru naturalexit0. Six640×480readbacks(full/half/low) viewed.
Changed pixels:Ko24133/167218/167200,Ru21148/167236/167200. Profiles intentionally
use distinct localized main art;frame equality is not assumed. Half/low frames
also exercise tagged close/title RGB preservation.

Production SHA256
`0def3dce864ffe438eddf73abd84e17929121d2abb06f19921c8d37f9ef26e37`,
x86/base400000/entry14EFF0,2033664bytes,182client/20kernel/27facade TU,
0unresolved. Production map retains CGUIMiniMapWindow.ScrollEvent/SetAlpha455,
CGUIScrollbarEX.SetAmount and new opacity facade. EX is no longer unused;
Var can still be stripped. Sourcegenerator idempotent;engine unchanged.

Ordinary scrollbar,EX/Var,textboard,textmetrics,font,modal andtutorial-board
regressions passed. Exact own WinMain/TCPfixture/engine/D3D/Character/existingCreate1
passed and stopped before game loop. Seven scoped gates remain PARTIAL. No
unchanged large particle/runtime suite rerun.

Evidence: `inventory/client455-minimap-opacity-{reference,native,checkpoint}.json`;
raw ignored `artifacts/client455-tutorial/minimap-*067.json`;
labs `work/m9/c8d0f03b/opacity-{ko-kr,ru-ru}-001`.

Next068:target GUIObject/Container input/show/focus/parent wiring. Start from
Add60BFA0 and helper60D3D0,observer setters60A450/6300C0,SendMouse*/InputProc.
Ordinary065 SetAmount assembly registers only self,EX066 hasfour explicit
registrations. Do not assume their private wiring is interchangeable. Own0.7
parent path is tested;full455 pipeline is not proved. Then production rich text/
message sizing/fullbriefing and actual Tutorial/fourstage. Fullminimap/camera/
other M6F/M7/M9 remain OPEN;graphics modernization M8 outside scope.
