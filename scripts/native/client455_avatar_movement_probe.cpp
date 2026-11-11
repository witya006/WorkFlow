#include "gameobject/manager/ccharactermgr.h"
#include "gameobject/manager/ctargetmgr.h"
#include "network/cnetworkmgr.h"

#include <array>
#include <cstdio>
#include <limits>
#include <memory>
#include <stdexcept>
#include <vector>

namespace {
void require(bool condition, const char* message)
{
    if (!condition) throw std::runtime_error(message);
}

template<class Tag, typename Tag::Type Member>
struct MemberAccess { friend typename Tag::Type access(Tag) { return Member; } };
struct SendBuffer { using Type = _NET_BUFFER* CNetProcess::*; friend Type access(SendBuffer); };
struct Owner { using Type = CNetWorking* CNetProcess::*; friend Type access(Owner); };
struct Active { using Type = BYTE(CNetworkMgr::*)[6]; friend Type access(Active); };
template struct MemberAccess<SendBuffer, &CNetProcess::m_pSendBuffer>;
template struct MemberAccess<Owner, &CNetProcess::m_pNetwork>;
template struct MemberAccess<Active, &CNetworkMgr::m_activeServer455>;

struct Network : CNetworkMgr {
    using CNetworkMgr::AnalysisServerPacket;
    using CNetworkMgr::m_movement455;
    using CNetworkMgr::SendAvatarMove455;
};

struct SendRing {
    CNetProcess& process;
    _NET_BUFFER buffer;
    std::vector<char> storage;
    RF455NetworkCodec peer;

    explicit SendRing(Network& network) : process(network.m_Process[0]), storage(10000)
    {
        require(buffer.Configure(10000, 10000, storage.data()), "send ring storage");
        process.*access(SendBuffer{}) = &buffer;
        process.*access(Owner{}) = &network;
        process.m_nIndex = 0;
        process.m_Type.m_wSocketMaxNum = 1;
        process.m_codec455.initializeDefault(true);
        process.m_NetSocket.GetSocket(0)->m_bAccept = true;
        peer.initializeDefault(true);
        peer.receiveKey = process.m_codec455.sendKey;
        (network.*access(Active{}))[0] = 0;
    }

    ~SendRing()
    {
        process.m_NetSocket.GetSocket(0)->m_bAccept = false;
        process.*access(SendBuffer{}) = nullptr;
        process.*access(Owner{}) = nullptr;
    }

    void Expect(BYTE opcode, const std::vector<BYTE>& expected)
    {
        int size = 0;
        bool empty = false;
        const auto* wire = buffer.GetSendPoint(&size, &empty);
        std::array<BYTE, 64> decoded{};
        std::size_t produced = 0;
        require(wire && !empty && peer.decode(wire, size, decoded.data(), decoded.size(), produced) &&
                produced == expected.size() + 4 && decoded[2] == 4 && decoded[3] == opcode,
                "ordinary transport group, opcode and exact payload length");
        // Independent inverse of the transform for the test's nonzero seed.
        for (std::size_t index = 0; index < expected.size(); ++index) {
            const BYTE restored = static_cast<BYTE>((decoded[4 + index] ^ BYTE(0x31 + opcode + 32)) - 31);
            require(restored == expected[index], "position payload byte");
        }
        buffer.AddPopPos(size);
    }
};

template<class Value>
void put(std::vector<BYTE>& bytes, std::size_t offset, Value value)
{
    std::memcpy(bytes.data() + offset, &value, sizeof(value));
}

int run()
{
    ChInterface renderer;
    g_ifCharIF = &renderer;
    require(_CreateAnimationMgr(), "normal animation owner");
    auto network = std::make_unique<Network>();
    auto avatar = std::make_unique<CAvatar>();
    g_pAvatar = avatar.get();
    avatar->SetCharTypeID(CTI_AVATAR);
    avatar->SetIndex(0x100);
    avatar->SetClientStage455(3);
    avatar->SetWalkMode(CMM_MOVE_RUN);
    avatar->SetSpeed(72.5f);
    avatar->CCharacter::SetAction(CAI_MOVE_STOP);
    avatar->SetPosition(-1200.75f, 67.25f, 493.125f, TRUE, TRUE);
    CNextActionMgr next;
    g_pNextActionMgr = &next;
    network->m_account455.delta = 7;
    network->m_account455.mask = 0x2131;
    SendRing ring(*network);
    auto& state = network->m_movement455;

    const auto dispatch = [&](BYTE opcode, std::vector<BYTE>& bytes) {
        _MSG_HEADER header{WORD(bytes.size() + 4), {4, opcode}};
        return network->AnalysisServerPacket(&header, reinterpret_cast<char*>(bytes.data()));
    };
    constexpr float target[]{-1180.875f, 67.25f, 521.75f};
    require(network->SendAvatarMove455(target) && state.pending && state.stopArmed,
            "nonpredictive request waits");
    require(!network->SendAvatarMove455(target), "pending request suppresses duplicate");
    std::vector<BYTE> move(26, 0);
    move[0] = 1;
    put(move, 1, -1200.75f);
    put(move, 5, 67.25f);
    put(move, 9, 493.125f);
    put(move, 13, std::uint32_t{1});
    put(move, 17, std::int16_t{-1180});
    put(move, 19, std::int16_t{521});
    put(move, 22, 72.5f);
    ring.Expect(1, move);

    std::vector<BYTE> correction(13, 0);
    correction[0] = 7;
    put(correction, 1, -1195.5f);
    put(correction, 5, 67.25f);
    put(correction, 9, 497.75f);
    require(dispatch(3, correction) && !state.pending && !state.pendingAt &&
            avatar->GetPosX() == -1195.5f, "correction clears wait and applies position");

    std::vector<BYTE> sample(16, 0);
    put(sample, 0, std::uint32_t{2});
    put(sample, 4, -1195.5f);
    put(sample, 8, 67.25f);
    put(sample, 12, 497.75f);
    require(network->PositionMsg_RealMovposRequest_clzo(), "position report sent");
    ring.Expect(2, sample);
    put(sample, 0, std::uint32_t{3});
    require(network->PositionMsg_PlayerStop_clzo(TRUE) && !state.stopArmed,
            "one stop closes moving state");
    ring.Expect(19, sample);
    require(!network->PositionMsg_PlayerStop_clzo(TRUE) && state.sequence == 4,
            "no repeated stop packet");

    std::vector<BYTE> stop(10, 0);
    put(stop, 0, std::uint32_t{0x100}); // Old route misread the zero low byte as teleport success.
    put(stop, 4, std::int16_t{-1194});
    put(stop, 6, std::int16_t{67});
    put(stop, 8, std::int16_t{498});
    require(dispatch(20, stop) && next.IsEmpty() && avatar->GetPosX() == -1195.5f,
            "near stop result never enters map-transfer handler");
    put(stop, 4, std::int16_t{-1150});
    require(dispatch(20, stop) && next.GetNextAction() == CAI_MOVE_MOVING &&
            next.GetNextTargetPosition()[0] == -1150 && avatar->GetPosX() == -1195.5f,
            "distant stop queues position without snapping");
    stop.resize(9);
    require(!dispatch(20, stop), "truncated stop is rejected");

    state.predictLocally = true;
    require(network->SendAvatarMove455(target) && !state.pending, "predictive request never latches");
    put(move, 1, -1195.5f);
    put(move, 9, 497.75f);
    put(move, 13, std::uint32_t{4});
    ring.Expect(1, move);
    std::vector<BYTE> broadcast(17, 0);
    put(broadcast, 0, std::uint32_t{0x100});
    require(dispatch(4, broadcast) && avatar->GetPosX() == -1195.5f,
            "predictive avatar ignores a position echo");
    broadcast.resize(16);
    require(!dispatch(4, broadcast), "truncated move is rejected");
    const float invalid[]{std::numeric_limits<float>::infinity(), 0, 0};
    require(!network->SendAvatarMove455(invalid) && state.sequence == 5, "nonfinite target is rejected");

    g_pNextActionMgr = nullptr;
    g_pAvatar = nullptr;
    _DestroyAnimationMgr();
    g_ifCharIF = nullptr;
    std::puts("{\"status\":\"PASS\",\"move_bytes\":26,\"position_bytes\":16,"
              "\"stop_bytes\":16,\"stop_result_bytes\":10,\"move_result_bytes\":17,"
              "\"exact_transport_bytes\":true,\"pending_correction\":true,\"local_stop_threshold\":10}");
    return 0;
}
}

int main()
{
    SetErrorMode(SEM_FAILCRITICALERRORS | SEM_NOGPFAULTERRORBOX | SEM_NOOPENFILEERRORBOX);
    try {
        return run();
    } catch (const std::exception& error) {
        std::fprintf(stderr, "%s\n", error.what());
        return 1;
    }
}
