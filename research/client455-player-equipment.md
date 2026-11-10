# Player equipment146 — source component,production integration open

Status:PARTIAL_COMPONENT. Ordinary runtime stays145,ownPE SHA256
1a3553721149f8638812d636e2dfa3053d75b58a58c6310df72478050ab5670d.
No full appearance,selection or M6/M9 acceptance is claimed.

## Reference and implementation

Pinned x86/base400000 primary SHA256
b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b;
secondary46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.
32full functions/1640instructions/225positiveCFG blocks match both binaries.
Evidence includes PlayerProc RTTI/vtable and CNormalItem Clone RTTI/vtable.
Full regions/RVAs/hashes:inventory/client455-player-equipment-reference.json.
Raw:artifacts/client455-progress/player-equipment146-reference/session.json.

Recovered source:client455_player_equipment.h andclient455_normal_item_copy.h.
The controller owns13typed resource slots and requires explicit host providers.
It is not yet added to ordinary CPlayerProc;providers have no default/no-op bodies.

- RVA53030/53100/531E0: numeric,board-wrapper andequipment-wrapper equip paths.
- RVA53760/53AF0/53C40: creation andwrapper-sharing paths;internal9/10/11
 rejected except10/index<80. Type46→slot9;type27→slot11;type5/index<80→hair10.
 Factorytypes forslots9/10/11 are46/5/27;slot12 is valid storage.
- Race is ORed into bits28..31;actual Item/Resource/mesh lookups are reused.
 The mesh may be absent while metadata creation still succeeds,as in145.
- A failed resource creation clears the wrapper;failed payload factory retains
 the successful resource creation and its nonempty index,without a payload.
- Slot9 writes ownerbyte5180 frommetadata176 and skips animation. Slot8 gets
 animation0;other slots except9 getanimation1. Weapon scaling can happen twice
 in wrapper overloads,once in core creation andagain in the wrapper path.
- RVA53A80 is NOT Player.SetPrevAction. Full ASM ofcall4539BD shows equipment
 this andplayer arg0;it stores ownerpointer atobject588. The decompiler signature
 misleadingly obscured the this register. The source stores the real own player.
- RVA536C0/53730:aliases in getters,wrapper emptiness check thenpayload access.
 Getter5 does not remap a low-index helmet tohair10.
- RVA53280:weapon/shield/additional weapon rematch,fadeguard3/1 inpeace or4/2
 incombat,duration60;shield skips action repetition. Numeric/board type27index>=30
 uses the direct rematch branch;equipment-wrapper overload uses the ordinary branch.
- RVA53550:clone first,detach event2 forkind8/46,clear wrapper,apply removal
 using the detached clone,delete clone;repeat action forslot6/11 ifactiontype1.
 Item kind comes frommetadata88(RVA10FA0),not CItem header kind12.
- CNormalItem Clone RVA61CC0 allocates200bytes;copy ctor4BC0→5CE0→5E70
 copies selected fields andthe existing reference byte. It neither retains the
 original norinserts the detached clone into the manager. Unwritten padding is
 not normalized or copied wholesale.

## Real execution and limits

Own full-object native probe links the exact145client/engine object set.
Actual Item47/Resourcecatalog/D3D9/Characterowners are loaded.30base model
creations through the controller cover six parts/five races,with actual mesh
bindings andplayer ownerpointer.32selected modelrecords and33GPUtexture entries
are checked by the shared real-resource run.

Additional real metadata checks cover slots8/9/10/11/12,type27/46 aliases,
reserved/bounds errors,failed factory/failed metadata replacements andboth
wrapper overloads. Weapon/shield callbacks have expected order fromfullASM.
Copy consumers still read original IDs,metadata,name andreference byte after
slot release. Shared-source wrappers retain/release one reference correctly;
allpayloads are gone afterteardown.

The native host uses actual mesh-parent rematching andthe reconstructed normal
clone. Its animation,fade/action,condition/effect callbacks record invocations;
their gameplay bodies are NOT accepted orconnected toordinary CPlayerProc.
Special-slot model/texture appearance is not proved by metadata checks.
The output explicitly reports production_controller_connected=false and
full_player_appearance_or_draw=false.

No reference EXE orserver source was executed/modified. Inputs use the existing
owned shared pool:1685references/166052882logicalbytes,newpoolbytes0 onthisrun.
No old work directories deleted. Before146 preserves exact145runtime(50files).
IDA7c61237d saved/closed;finalsessionlist0;allownnativeprocesses terminal0.

Reproduce:audit_client455_player_equipment.py →probe_client455_player_equipment.py
→checkpoint_client455_player_equipment.py,through scripts/Invoke-Python.ps1.
Gate:inventory/client455-player-equipment-checkpoint.json (component only).
Ordinaryruntimegate remains inventory/client455-equipment-checkpoint.json.

## Continue146 toward actual appearance

1. Restore required production equipment animation/effect/condition providers,
 especially46DF10→46D2F0→46D730 and46D3D0,4411E0 andits typed consumers.
2. Connect the controller toactual CPlayerProc/CPlayer/Avatar andregistered
 receiver. Migrate GetNormalItem/upgrade writes with the real455payload API;
 do not cast raw metadata intolegacy CNormalItem/ITEM_DATA.
3. Restore actual frame/animation/render loops,appearance filters anddefault
 substitution,thenverify equipped characters in the ordinary selection route.
 Diagnostic pcode suggests12rendered slots despite13stored slots;collectfull
 ASM/CFG/equality before implementing these render branches.
4. Continue remaining bootstrap,selection andworld;M6/M6F/M7/M9 stayOPEN.

Provider diagnostic pcode is saved separately inproviders-diagnostic.json;
441AC0 is incomplete andrequires cursor100 continuation. None ofthis diagnostic
file is claimed asfullASMconfirmed. Overall estimate25%(20–35%)unchanged.
