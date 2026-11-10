"""Reproduce the installed launcher's local auth wire;never persist credentials."""
import argparse,base64,datetime,getpass,hashlib,json,socket,struct,sys
from pathlib import Path
from compare_client_binaries import WS


def string(value):
    data=value.encode('utf-8')[:1024]
    return struct.pack('<H',len(data))+data


def auth_request(login,password):
    login=login.strip();email,account=(login,'') if '@' in login else ('',login)
    payload=string(email)+string(account)+string(password)+b'\0'
    return struct.pack('<HBB',len(payload)+4,0x6c,3)+payload


def read_string(data,offset):
    if offset+2>len(data):raise ValueError('Missing launcher string length')
    size=struct.unpack_from('<H',data,offset)[0];offset+=2
    if offset+size>len(data):raise ValueError('Truncated launcher string')
    return data[offset:offset+size].decode('utf-8'),offset+size


def auth_reply(data):
    if len(data)<5:raise ValueError('Truncated auth reply')
    accepted=data[0]!=0;account=struct.unpack_from('<I',data,1)[0]
    identifier,offset=read_string(data,5);message,offset=read_string(data,offset)
    key=''
    if offset<len(data):key,offset=read_string(data,offset)
    if offset!=len(data):raise ValueError('Unexpected auth reply tail')
    decoded=bytes.fromhex(key[4:]) if key.startswith('rf1:') and len(key)==36 else b''
    return accepted,account,identifier,message,decoded


def receive(peer,size):
    out=bytearray()
    while len(out)<size:
        data=peer.recv(size-len(out))
        if not data:raise ValueError('Launcher peer closed before complete frame')
        out+=data
    return bytes(out)


def marshal_v4x(account,identifier,key):
    if len(key)!=16:raise ValueError('Missing live world key')
    raw=bytearray(93);address=struct.unpack('<I',socket.inet_aton('127.0.0.1'))[0]
    struct.pack_into('<I',raw,0,address^0xcb9c4b3a);struct.pack_into('<H',raw,4,27830^0x4fb6)
    identifier=(identifier or 'acc').encode('utf-8')[:12];raw[6:6+len(identifier)]=identifier
    struct.pack_into('<I',raw,57,account^0x6e65e0af)
    masks=[0xcfcf22e6,0x5bbcde6f,0xacdf5eda,0xbccd1b37]
    for i,mask in enumerate(masks):struct.pack_into('<I',raw,61+4*i,struct.unpack_from('<I',key,4*i)[0]^mask)
    struct.pack_into('<H',raw,77,0^0x4b3a);struct.pack_into('<I',raw,79,account^0xc89c183a)
    struct.pack_into('<I',raw,83,0xc89c183a);struct.pack_into('<H',raw,91,8^0x32d7)
    return bytes(raw)


def selfcheck():
    assert auth_request('ab','c')==bytes.fromhex('0e006c0300000200616201006300')
    sample=b'\1'+struct.pack('<I',7)+string('abc')+string('')+string('rf1:'+bytes(range(16)).hex())
    result=auth_reply(sample)
    assert result[:4]==(True,7,'abc','') and result[4]==bytes(range(16))
    for malformed in [b'',sample[:4],sample[:6],sample[:-1],sample+b'\0']:
        try:auth_reply(malformed)
        except ValueError:pass
        else:raise AssertionError('Malformed launcher reply accepted')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--authenticate',action='store_true');parser.add_argument('--interactive',action='store_true');parser.add_argument('--own-login',action='store_true');args=parser.parse_args()
    selfcheck()
    if not args.authenticate:
        print('PASS:small valid/malformed launcher-wire examples');return
    #stdin rather than commandline/environment/source files. Neither the raw
    #request norreply,account identifier,message orlogin key is logged. A live
    #run writes only the game's private temporary handoff and removes it.
    print('Awaiting test credentials on stdin',flush=True)
    #URL-safe base64 avoids console key-translation of JSON punctuation.
    raw=base64.urlsafe_b64decode(getpass.getpass('Test credentials base64 (hidden): ')).decode('utf-8') if args.interactive else sys.stdin.readline()
    secret=json.loads(raw);del raw
    login=secret.pop('login');password=secret.pop('password')
    if not isinstance(login,str) or not isinstance(password,str):raise ValueError('Invalid credential types')
    request=auth_request(login,password);del secret,login,password
    with socket.create_connection(('127.0.0.1',27831),timeout=8) as peer:
        peer.settimeout(8);peer.sendall(request);del request
        header=receive(peer,4);size,category,kind=struct.unpack('<HBB',header)
        if not 4<=size<=4096 or (category,kind)!=(0x6c,4):raise ValueError('Unexpected launcher frame')
        data=receive(peer,size-4)
    accepted,account,identifier,message,key=auth_reply(data)
    #ServerClient.Login checks accepted,not account!=0. Account serial zero
    #andthe optional key's value must not be mistaken for auth failure.
    complete=len(key)==16
    report=dict(scope='One actual launcher authentication exchange withthe user-started local v0.4.0;not ownRFgame authentication',
        time_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),endpoint=dict(host='127.0.0.1',port=27831),
        request_kind='6C/03',reply_kind='6C/04',reply_bytes=size,accepted=accepted,complete_login_key_received=complete,
        has_game_identifier=bool(identifier),login_key_bytes=len(key),
        launcher=dict(file='E:/RFOnlineTrash/RFOnline/rflauncher.exe',sha256=hashlib.sha256(Path('E:/RFOnlineTrash/RFOnline/rflauncher.exe').read_bytes()).hexdigest()),
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),credentials_persisted=False,raw_packets_persisted=False,
        game_executable_started=False,server_files_modified=False,full_RF_protocol_verified=False,M6='OPEN',M9='OPEN')
    if args.own_login and accepted and complete:
        handoff=marshal_v4x(account,identifier,key);del data,account,identifier,message,key
        import probe_client455_device_startup
        old_arguments=sys.argv
        try:
            sys.argv=['probe_client455_device_startup.py','--login-frame','--settle-ms','8000','--with-lobby','--nation','Taiwan']
            try:game=probe_client455_device_startup.main(handoff=handoff,live_port=27830)
            except SystemExit:
                game=json.loads((WS/'inventory/client455-login-frame-live-taiwan-native.json').read_text())
            report['own_live_run']={'report':'inventory/client455-login-frame-live-taiwan-native.json','reached_Login':game['reached_first_login'],'private_handoff_removed':game['live_server']['private_handoff_removed']}
            report['game_executable_started']=True
            report['scope']='Actual local launcher authentication followed by an own-client live handoff observation;not full game authentication acceptance'
        finally:sys.argv=old_arguments;del handoff
    else:del data,account,identifier,message,key
    (WS/'inventory/client455-live-launcher-native.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))
    if not accepted or (args.own_login and not report.get('own_live_run',{}).get('reached_Login')):raise SystemExit(1)


if __name__=='__main__':main()
