"""Migrate ordinary item-wrapper ownership while keeping mixed consumers explicit."""
import re

def port_item_object(raw,relative,native,section):
    changed=False
    if relative=='mainapp.h':
        raw=b'#include "client455_client_items.h"\r\n'+raw
        anchor=b'\tCLand\t\t\t\t\tm_cLand;'
        if raw.count(anchor)!=1:raise ValueError('MainApp item owner order changed')
        raw=raw.replace(anchor,b'\tRF455ClientItems m_items455;\r\n'+anchor)
        anchor=b'\tBOOL\tGameMainLoop( void );'
        if raw.count(anchor)!=1:raise ValueError('MainApp item runtime API changed')
        raw=raw.replace(anchor,anchor+b'\r\n\tRF455ClientItems& Items455(){return m_items455;}');changed=True
    elif relative=='item/citemdata.h':
        raw=b'#include "client455_item_object.h"\r\n'+raw
        begin=raw.index(b'class CBoardObject : public CObject');end=raw.index(b'\n};',begin)+3
        raw=raw[:begin]+(native/'client455_board_object.inc').read_bytes()+raw[end:]
        for cls,kind in [('CBoardItem','BOT_BOARD_ITEM'),('CSFItem','BOT_SF'),('CAnimusItem','BOT_ANIMUS'),('CUnitPartsItem','BOT_UNIT_PARTS'),('CUnitItem','BOT_UNIT_FRAME')]:
            anchor=('\t'+cls+'();').encode()
            if raw.count(anchor)!=1:raise ValueError('Legacy item constructor declaration changed:'+cls)
            raw=raw.replace(anchor,anchor+('\r\n\tBYTE GetItemType() override{return '+kind+';}').encode())
        changed=True
    elif relative=='item/citemdata.cpp':
        for signature in [b'CBoardObject::CBoardObject(',b'CBoardObject::~CBoardObject(',b'CBoardObject::IsEqual( DWORD',b'CBoardObject::IsEqual( CBoardObject',b'CBoardObject::BeginDelayAnimation(']:
            begin,end=section(raw,signature,signature)
            # section starts at the qualified name,so remove the preceding
            # legacy return type where one exists as well.
            before=raw[:begin]
            match=re.search(rb'(?:BOOL|void)\s*$',before)
            if match:begin=match.start()
            raw=raw[:begin]+raw[end:]
        raw=re.sub(rb'\tm_byItemType\s*=\s*BOT_[A-Z_]+;',b'',raw)
        for cls in ['CBoardItem','CSFItem','CAnimusItem','CUnitPartsItem']:
            begin,end=section(raw,(cls+'::Clear(').encode(),(cls+'::Clear(').encode());body=raw[begin:end]
            at=body.index(b'{')+1;raw=raw[:begin]+body[:at]+b'\r\n\tCBoardObject::Clear();'+body[at:]+raw[end:]
        # Explicit Clone retains after copy,as46B570. Parent copy alone does not.
        for cls in ['CBoardItem','CSFItem','CAnimusItem','CUnitPartsItem','CUnitItem']:
            begin,end=section(raw,(cls+'::Clone(').encode(),(cls+'::Clone(').encode())
            body=(cls+'::Clone(){auto* result=new '+cls+'(*this);result->RetainSharedItem455();return result;}').encode()
            raw=raw[:begin]+body+raw[end:]
        changed=True
    return raw,changed
