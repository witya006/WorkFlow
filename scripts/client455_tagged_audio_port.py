"""Own tagged audio service in the ordinary client; legacy engine remains intact."""


def port_tagged_audio(raw,relative,section):
    if relative=='mainapp.h':
        raw=b'#include "client455_tagged_audio.h"\r\n#include "client455_event_music.h"\r\n#include "client455_event_music_play.h"\r\n'+raw
        old=b'RF455IconLinks m_iconLinks455;'
        if raw.count(old)!=1:raise ValueError('Tagged audio owner boundary')
        raw=raw.replace(old,old+b'\r\n\tRF455TaggedAudio m_taggedAudio455;\r\n\tRF455EventMusicCatalog m_eventMusic455;\r\n\tRF455EventMusicPlayer m_eventMusicPlayer455;')
        old=b'RF455IconLinks& IconLinks455(){return m_iconLinks455;}'
        if raw.count(old)!=1:raise ValueError('Tagged audio API boundary')
        raw=raw.replace(old,old+b'\r\n\tRF455TaggedAudio& TaggedAudio455(){return m_taggedAudio455;}\r\n\tRF455EventMusicCatalog& EventMusic455(){return m_eventMusic455;}\r\n\tRF455EventMusicPlayer& EventMusicPlayer455(){return m_eventMusicPlayer455;}')
        return raw,True
    if relative=='mainapp.cpp':
        old=b'InitR3SoundSystem('
        if raw.count(old)!=1:raise ValueError('Tagged audio search before Miles startup')
        raw=raw.replace(old,b'RF455_PrepareTaggedAudio(GetR3State()->SoundPath);\r\n\t'+old)
        startup=b'InitR3SoundSystem(".\\\\snd\\\\WaveList.spt");'
        if raw.count(startup)!=1:raise ValueError('455 BGM startup boundary')
        raw=raw.replace(startup,startup+b'\r\n\tg_MainApp.EventMusic455().loadBgm("./Snd/BGMList.spt");')
        shutdown=b'\tReleaseR3SoundSystem();'
        if raw.count(shutdown)!=1:raise ValueError('455 event music driver shutdown boundary')
        raw=raw.replace(shutdown,b'\tg_MainApp.EventMusicPlayer455().Clear();\r\n'+shutdown)
        start,end=section(raw,b'CMainApp::Create(',b'CMainApp::Create(')
        body=raw[start:end];old=b'm_cLand.Create();'
        if body.count(old)!=1:raise ValueError('Tagged audio Create boundary')
        body=body.replace(old,b'if(!m_taggedAudio455.Open(".\\\\Snd\\\\WaveList.spt",GetR3State()->SoundPath))\r\n\t\tOutputDebugStringA("RF455 TaggedAudio:unavailable");\r\n\t'+old)
        raw=raw[:start]+body+raw[end:]
        start,end=section(raw,b'CMainApp::Destroy(',b'CMainApp::Destroy(');at=raw.index(b'{',start)+1
        raw=raw[:at]+b'\r\n\tm_eventMusicPlayer455.Clear();\r\n\tm_taggedAudio455.Close();\r\n\tm_eventMusic455.clear();'+raw[at:]
        raw+=b'''\nRF455EventMusicCatalog& RF455_GameEventMusicCatalog() { return g_MainApp.EventMusic455(); }
RF455EventMusicPlayer& RF455_GameEventMusicPlayer() { return g_MainApp.EventMusicPlayer455(); }
'''
        return raw,True
    if relative=='gameprogress/cgp_login.cpp':
        anchor=b'_GetLand()->LoadData();'
        if raw.count(anchor)!=1:raise ValueError('455 EventSound bootstrap boundary')
        raw=b'#include "client455_nation_paths.h"\r\n#include <string>\r\n'+raw
        raw=raw.replace(anchor,b'''const auto* nationPaths455 = RF455_GetNormalNationPaths();
                if (nationPaths455->configured) {
                    const auto events = std::string(nationPaths455->dataRoot) + "/EventSound.edf";
                    _GetMainApp()->EventMusic455().loadEventSound(events.c_str());
                }
                '''+anchor)
        return raw,True
    if relative=='gameobject/manager/ccharactermgr.cpp':
        marker=b'\tCacheArrangementByTime();'
        if raw.count(marker)!=1:raise ValueError('455 event music observation boundary')
        raw=raw.replace(marker,b'''    auto& eventMusic = RF455_GameEventMusicPlayer();
    const auto& catalog = RF455_GameEventMusicCatalog();
    eventMusic.BeginObservation();
    if (catalog.hasEventTracks()) {
        const auto& data = RF455_GameItems().data;
        for (auto* actor : m_listActive[CTI_MONSTER]) {
            if (!actor || actor->IsEnable(ROSF_DESTROY) || actor->IsDeath() ||
                actor->IsEnable(ROSF_OUT_OF_VISUAL_FIELD_SERVER) ||
                actor->IsEnable(ROSF_OUT_OF_VISUAL_FIELD_CLIENT)) continue;
            std::uint32_t code = 0, slot = 0;
            if (RF455_EventMusicMonsterCode(data, actor->GetDTIndex(), code) &&
                catalog.trackForMonster(code, slot))
                eventMusic.Observe(slot, catalog.musicAt(slot));
        }
    }
    eventMusic.EndObservation();

'''+marker)
        return (b'#include "client455_event_music.h"\r\n#include "client455_event_music_play.h"\r\n'
                b'#include "client455_client_items.h"\r\n'+raw),True
    if relative=='addcodebyjang/effectutil.cpp':
        start,end=section(raw,b'void EFUtil_MusicLoop()',b'void EFUtil_MusicLoop()')
        body=raw[start:end]
        at=body.index(b'{')+1
        body=body[:at]+b'''
    auto& eventMusic = RF455_GameEventMusicPlayer();
    eventMusic.Tick(R3GetLoopTime());
    const auto mapGain455 = eventMusic.MapGain();
'''+body[at:]
        faded=b'stPlayMP3[stOldPlayID].SetVolumeMP3(temp);'
        if body.count(faded)!=1:raise ValueError('455 ordinary map track volume boundary')
        body=body.replace(faded,b'stPlayMP3[stOldPlayID].SetVolumeMP3(temp * mapGain455);')
        played=b'stPlayMP3[stPlayID].PlayR3MP3();'
        if body.count(played)!=1:raise ValueError('455 ordinary map track start boundary')
        body=body.replace(played,played+b'\n                stPlayMP3[stPlayID].SetVolumeMP3(mapGain455);')
        at=body.rfind(b'}')
        body=body[:at]+b'''
    if (st_fMusicFadeCnt <= 0.0f && stPlayIndexName[stPlayID])
        stPlayMP3[stPlayID].SetVolumeMP3(mapGain455);
'''+body[at:]
        raw=raw[:start]+body+raw[end:]
        start,end=section(raw,b'void EFUtil_MusicEnd()',b'void EFUtil_MusicEnd()')
        at=raw.index(b'{',start,end)+1
        raw=raw[:at]+b'\n    RF455_GameEventMusicPlayer().Clear();'+raw[at:]
        return b'#include "client455_event_music_play.h"\r\n'+raw,True
    return raw,False
