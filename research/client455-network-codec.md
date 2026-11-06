# M6 / Network codec051

2026-11-06. Client reconstruction only. M6/M6F/M7/M9 remain OPEN.

The ordinary client source now uses recovered directional AES-CBC framing in
CNetProcess::LoadSendMsg and _PopRecvMsg. It configures two network processes
with capacity for six and uses dynamically allocated80-byte ring records with
20,000-byte receive rings and1,000,000-byte send rings. This does not establish
the complete455 transport, its message handlers, authentication or online play.

## Reference

Current SHA-256 `b1b5febf0d0394712e2322350e19dafe60742e8642697b93cfb89135bac1fd8b`;
backup `46528aac20499e3b3928d58658d7e0cefe26feba7cd193796d5cfbf7a2bbc558`.
Both x86/base0x400000. Thirty-three selected function ranges and seven data
ranges match in both pins. Input binaries were read, never executed.

| Contract | RVA | Evidence |
|---|---|---|
| Network configuration/creation | 0x161000,0x162020,0x162110,0x4a9da0,0x4aeb70 | Two236-byte configurations; six process capacity; receive20KB/send1MB; send worker always starts |
| Cipher selection | 0x4aa170,0x4aa1a0,0x4af880 | Per-process flag; configuration0 selects VCAES, configuration1 retains the default/no cipher |
| AES blocks / CBC wrappers | 0x4aa500,0x4aaa70,0x4ab090,0x4ab2b0 | AES tables/rounds, zero IV for every call, zero fill for a partial last block |
| Send framing / wrapper | 0x4acc60,0x162be0 | Plain four-byte header, encrypted outer length/padding, process0 flag disabled for group21 and enabled otherwise |
| Ring extraction / receive | 0x4ac3d0,0x4af480 | Two-byte plain or three-byte encrypted prefix, fragmented input, wrap, wire consumption independent of decoded header length |
| Ring setup/counters | 0x4ac260,0x4ac2f0,0x4ac330,0x4adc80 |80-byte record, main/extra capacities, borrowed scratch, push/pop counters and wrap |

Default encryption/decryption round counts are both12: AES192. The schedules
at RVA0x7d1d70/0x7d1c78 differ. The audit canonicalizes the little-endian DWORD
storage, reverses the inverse schedule and verifies both complete208-byte active
expansions against independently generated AES192 schedules. Static protocol
constants are generated only under ignored work/ and included in the owned
build. Tracked manifests record hashes; no account/session data is involved.

The plain packet is LE16 total length, group byte, opcode byte, payload. Its
encrypted form is LE16 outer length, one-byte zero-padding count, then CBC
ciphertext. Padding makes the inner packet a multiple of16; an already aligned
packet receives no extra block. The padding is not PKCS. Decryption removes
the outer prefix/padding and dispatches the inner header/payload. The receive
ring advances by the original wire length.

Disassembly clarifies a dangerous target detail: Create passes Src+472 to the
cipher selector for process2 even though its local configuration array has
two elements. The selector writes at+228/+232. The source port configures the
two real processes and does not reproduce that stack overwrite. This unsafe
domain remains explicitly outside the current equivalence evidence.

## Implementation

- `client455_network_codec.{h,cpp}`: readable AES expansion/block operations,
  independent send/receive keys, bounded packet encoder and decoder. Production
  uses source AES; Windows CNG is only the independent native-test oracle.
- `client455_network_buffer.inc`:80-byte ring record with owned main allocation,
  borrowed process scratch, fragmentation/wrap handling and DWORD counters.
- `client455_network_send.inc`: actual normal sender encodes before queueing.
- `client455_network_config.inc`: two configured TCP processes, one socket and
  one receive worker each, confirmed base timeouts/sleep values; process0 has
  the default cipher and process1 has none. Network capacity grows from3to6.
- `prepare_client455_normal.py`: integrates those files, receive decoding and
  wire-length advancement. SetNetSystem propagates SetProcess failure and the
  normal CNetworkMgr::Create returns the transport creation result. Old12 game
  handlers remain; none are replaced with success stubs.

The current transport still uses legacy event/thread/internal-message logic.
Its full236-byte configuration semantics, queued route, send filters/throttle,
backpressure and error/lifetime behavior are not certified. Buffer ownership is
source-owned, without casting the old classes onto target private layouts.

## Verification

Own full-object native probe, linked to the same182 normal client objects:

- AES128/192/256 block operations compared against Windows BCrypt AES-CBC with
  zero IV; source decryption and in-place block decryption also checked.
- Both real directional192-bit keys compared with independent CNG framing over
  16 selected payload sizes, including block edges and large valid packets.
  Truncated/malformed input and output capacity boundaries rejected explicitly.
- Actual CNetProcess sender queues the expected encrypted bytes across a send
  ring wrap. Actual _PopRecvMsg receives a packet in two fragments across a
  receive wrap, decodes it and calls the real virtual dispatch boundary with
  the expected inner header/payload; the wire bytes are consumed exactly once.
- Actual global CMainApp network creation yields two processes, capacity6,
 80-byte rings and the confirmed sizes. Actual SendNetMessage changes process0
  cipher state for group21 versus other groups even when the unconnected send
  fails. No listening service or authentication is simulated by these fixtures.
- The probe exits naturally with0. Windows CNG is not linked into RF_Online.bin;
  production retains its audited runtime dependencies.

Final own PE SHA-256
`71e644eb7948f54dcee7528ef69cefc59403d23cc49bfd656c77730abda5d405`;
x86/base0x400000/entryRVA0x149ef0,2,008,576bytes.182 client objects,
20 canonical kernels,20 facade units; link0 unresolved. Engine unchanged.
Exact own WinMain retains Korean/Russian language/bootstrap/Miles startup.
Existing CMainApp::Create returns1 at ownRVA0xb40d8 after CALL0xb40d3→0xb3730;
the debugger stops there before the game loop. This is not a complete455Create
or normal game-exit acceptance. Prior scoped regressions/checkpoints are retained.

Evidence: `inventory/client455-network-codec-{reference,native,checkpoint}.json`,
normal build/link and own startup reports. Raw IDA output remains ignored under
`artifacts/client455-network-codec/`. Owned session4c89c7ab closed/save=true.

## Remaining work / next052

Restore the client event pump/accept sequencing and the real pre-engine
ConnectToServer wait/timeout path (RVA0x3d1150). Verify a genuine TCP connection
as a transport scenario separately from game authentication. A raw0 return
does not prove connected: the previously confirmed close→GetLastError quirk
must still be handled through the target connected-state checks.

Recover the gate crypto request/response consumers (RVA0x169cd0/0x169d30),
remaining wire layouts and all35 message handlers. Request group21/opcode12
has no payload; the decoded response function stores a byte+1 and WORD+3,
but their full downstream meaning remains open. Old ID/password wire fields
still have13 bytes versus455state50/32. Full236-byte profile semantics,
standard/queued transport, threads, internal security messages, Close/error
paths, UI/login/gameplay/world/IME and full shutdown remain mandatory for M9.

Malformed/unsafe/OOM/overlap/concurrent domains and target stack corruption are
not certified as equivalent. Own guards prevent unsafe frame sizes and invalid
padding/inner-length use; valid packet evidence is not a claim about all inputs.
