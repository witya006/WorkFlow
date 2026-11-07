#pragma once
#include <cstdint>
#include <memory>
void RF455_PrepareTaggedAudio(const char* redist);
struct RF455TaggedWaveView {
    bool present=false;unsigned slots=0,cacheEntries=0,manifestRecords=0;
    void* sample=nullptr;void* data=nullptr;unsigned tag=0,kind=0,active=0,waveID=0;
    float relative[3]={};
};
// Source owner for the 455 tagged 3D-wave family. The old untagged 2D API is
// still a separate legacy consumer, not accepted as the rest of 455 audio.
class RF455TaggedAudio {
public:
    RF455TaggedAudio();~RF455TaggedAudio();
    RF455TaggedAudio(const RF455TaggedAudio&)=delete;
    RF455TaggedAudio& operator=(const RF455TaggedAudio&)=delete;
    bool Open(const char* manifest,const char* redist);
    void Close();bool IsOpen()const;
    void SetListener(const float* position);
    void Play(std::uint32_t id,std::uint32_t loop,std::uint32_t tag,const float* position);
    void PlayAtListener(std::uint32_t id,std::uint32_t loop,std::uint32_t tag);
    void Stop(std::uint32_t id,std::uint32_t tag);
    void Collect();
    RF455TaggedWaveView Inspect(std::uint32_t id,unsigned slot=0)const;
    const char* ProviderName()const;
private:
    struct State;std::unique_ptr<State> state;
};
