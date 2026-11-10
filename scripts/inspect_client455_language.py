"""Read selected positional NDLanguage strings from the verified owned payload."""
import argparse,hashlib,json,sys
from compare_client_binaries import WS
from audit_client455_language import records

def main():
    parser=argparse.ArgumentParser();parser.add_argument('ids',nargs='+',type=lambda value:int(value,0));parser.add_argument('--nation',type=int,default=0);args=parser.parse_args()
    manifest=json.loads((WS/'inventory/client455-language-reference.json').read_text());entry=next(row for row in manifest['files'] if row['nation']==args.nation)
    raw=(WS/entry['decoded']).read_bytes();assert hashlib.sha256(raw).hexdigest()==entry['decoded_sha256'];rows,_=records(raw)
    values=[]
    for index in args.ids:
        assert 0<=index<len(rows);ident,text=rows[index];values.append(dict(index=hex(index),record_id=ident,text=text.rstrip(b'\0').decode('cp'+str(entry['codepage']),errors='strict')))
    sys.stdout.reconfigure(encoding='utf-8');print(json.dumps(values,ensure_ascii=False))
if __name__=='__main__':main()
