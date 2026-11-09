"""Reuse a recorded visual review only for byte-identical fresh frame captures."""
import argparse,json
from pathlib import Path
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import check,require,sha
from compare_client_binaries import WS


def reuse(prefix,snapshot):
    native_file=WS/f'inventory/client455-{prefix}-native.json';native=json.loads(native_file.read_text())
    previous_native=WS/f'artifacts/client455-progress/client455-{prefix}-native-{snapshot}.json'
    previous_review=WS/f'artifacts/client455-progress/client455-{prefix}-visual-review-{snapshot}.json'
    old=json.loads(previous_native.read_text());review=json.loads(previous_review.read_text())
    require(review['reviewed'] and review['reviewed_frames']==5 and review['native_sha256']==sha(previous_native),'Verified previous visual review '+prefix)
    check(review['sheet']);before={Path(x['file']).name:x for x in old['frames']}
    require(len(native['frames'])==len(before)==5 and not native['natural_exit'] and native.get('status') in ['PASS','PASS_SELECTED'],'Completed fresh frame capture '+prefix)
    for row in native['frames']:
        oldrow=before[Path(row['file']).name]
        for item in [row,row['preview'],oldrow,oldrow['preview']]:check(item)
        require(row['sha256']==oldrow['sha256'] and row['preview']['sha256']==oldrow['preview']['sha256'],'Exact reviewed raw pixels and preview '+prefix)
    review.update(native_sha256=sha(native_file),frames=native['frames'],script_sha256=sha(Path(__file__)),
                  reused_from_review=record(previous_review),reused_from_native=record(previous_native),
                  reused_pixels_byte_equal=True,new_visual_inspection=False)
    file=WS/f'inventory/client455-{prefix}-visual-review.json';file.write_text(json.dumps(review,indent=2)+'\n')
    return record(file)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('prefix',nargs='+');parser.add_argument('--snapshot',required=True);args=parser.parse_args()
    for prefix in args.prefix:reuse(prefix,args.snapshot);print(prefix+':5 fresh frames byte-identical to previously reviewed pixels')


if __name__=='__main__':main()
