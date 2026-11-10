# Equipment providers146 —real ANI/pose/fade source

PARTIAL_COMPONENT. Ordinary145 ownPE unchanged:
1a3553721149f8638812d636e2dfa3053d75b58a58c6310df72478050ab5670d.
Production PlayerProc/appearance/selection andM6/M9 remainopen.

## Confirmed reference

Pinned x86/base400000 primarySHA256
b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b;
secondary46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558.
24complete functions/2220instructions/373positiveCFG blocks match both.
RVA/region hashes:inventory/client455-equipment-providers-reference.json.
Raw:artifacts/client455-progress/equipment-providers146-reference/session.json.

Full code now uses nativeIDA CFG andindependent nativeIDA instruction counts,
theninstalled MSVC dumpbin over every contiguous CFG region. Every decoded byte
is compared toPE data;every region must be completely consumed andeveryblock
start must be an instruction. Instruction count must equal IDA's own count.
This removes repeated small disassembly requests without accepting previewdata.
Compact analyze_batch previews were not used asfullassembly:some arrays were
shorter thanthe reported count evenwhentruncated=false.

## Source behavior

RF455PlayerEquipmentObject now implements:

- RVA6D730 ANI ID selection fromreal Item metadata meshDWORD72,race,category/
 user/part rules;group5. This remapdoes not apply the creation-specificrace14/15
 exception. Intermediate fullID is written before the lookup.
- RVA6D2F0 core:required effect callback first,thenID=FFFFFFFF/data=null,
 requested lookup,mode0 fallback ifneeded. Failure leaves the old boneframes;
 final lookupID remains. Success installs actualANI,event metadata,selectedmode,
 oldframe0/newframe160,animatingtrue andthe real virtual ResetAnimation.
- RVA6DF10 wrapper:kind8/46 flag256 enabled formode0/3,disabled for1/2/4/5.
 It deliberately ignores theinner selection result andreturns true. Type46
 owner lift followsmode1/4 add,2/5 subtract;mode3 adds once iffglobalpendingflag
 was set,thenconsumes it. No unconditional lift forother modes.
- RVA4B8F0/4B9B0 mounting height helper:race0/1=5.8f,2/3=5.0f,other=8.0f;
 existingmount withmetadata meshID bits8..15=1 multipliesby0.75.416940 reads
 meshDWORD72,not the Item table index. The previous provider used the wrong
 join input;four additional real mount cases distinguish these values.
- RVA6E220/6E3A0 realfade state:60defaultframes,mode1 decreases tomode3/alpha0,
 mode2 increases tomode4/alpha1;intermediate alpha=count/max andflag4enabled,
 terminalflag4disabled. These are no longer only recorded fade requests.

Required animation item-effect callback remains explicit;its46D3D0 body is
not replaced by a no-op inproduction. It is a recorder inthis nativeprobe.
The own test height provider changes a real CAvatar's position using the
reconstructed height helper;the globalpendingflag stillneeds ordinary binding.
The target animation loader's full UI/quit policy onfailedfiles is notaccepted.

## Actual resources andexecution

69real-input cases cover cloak5races×6modes,siegekit,mount4races,miningtool,
four real meshID/table-index height discriminators andone ordinaryarmor
component withno standalone itemANI.52actualANI files and16actualmodels
are accounted;all selected model/ANI/texture paths resolve
throughloosefiles orRFS.16models are loaded forselection/pose checks,notfull
assembled-character appearance.

Native full-object run:68successful selections/68actualCResObject.Animation
pose calls,1expected no-ANI failure,86corelookups and24actual ownerheight changes.
The lookupcounter covers coreselection calls;wrapper repeatlookups are additional.
The publicwrapper returns true alsofor theexpectedinner failure. Modefallback,
frame preservation,renderflag,sharedpayload lifetime andactualfade transitions
pass. The affected13slotcontroller/clone probe was rebuilt afterthe classchange
andpasses;allpayloads are released afterteardown.

Real zero-maximum ANI is valid. Accretia cloakDEFAULT/USE/UNUSE andsiegekitDEFAULT
have maximum0 inindependently parsedfiles;the source preserves these values.
An initial probe incorrectly required maximum>0. The corrected oracle compares
the actual parsedmaximum,including0;the production animation code was not
changed toforce success. The failed run remains underwork/m9/476e69b4/.

Exporter texture directories cancontain KoreanANSIbytes. Basename extraction
is performed onbytes before decoding theresource-relative ASCIIbasename;
no recoding oforiginalfiles oraccess toobsolete exporterdrives occurred.

Current run:1747stagedassets/222051609logicalbytes;additional ownedpoolbytes
1974946. Earlier initialpool+53036735/repeat0 is historical. No wholeclientcopy orolddata
removal. Ordinary145PE/engine unchanged,soordinaryLogin was notrepeated.
IDA1049c6e2 saved/closed;finalsessionlist0;allnativehandles terminal0.
No referenceEXEexecution/serverchanges.

## Remaining integration

1. Item-animation effect ownership/cleanup/sound now has a separate verified
 source component:research/client455-equipment-effects.md. This ANI probe
 still records its effectcallback;the two components need actual integration
 andthe complete attachment-position provider.406CB0 is positionpointer+80,4077E0 isyaw+108;
 do notmislabel themname/scale basedondecompiler types.
2. Typed conditions4411E0/4412A0/441840/4418D0/441970/441AC0/442460.
 Their selectedfullASM is alreadyinthe24function proof,notjustpcode.
3. Connect actualCPlayerProc/CPlayer/Avatar/registered typed upgrades,then
 ordinary animation/render/defaultsubstitution/appearance/selection/bootstrap.
4. Full client acceptance,M6F/M7/M9;overall25%(20–35%)unchanged.

Next attachment diagnostics are saved initem-effects-diagnostic.json;they are
pcodeonly,notfullASMconfirmed.7E0D10's128lines are complete there.

Reproduce:decode_client455_cfg.py <ownedraw> →audit_client455_equipment_providers.py
→probe_client455_equipment_providers.py →checkpoint_client455_equipment_providers.py.
Use scripts/Invoke-Python.ps1. Gate:inventory/client455-equipment-providers-checkpoint.json.
