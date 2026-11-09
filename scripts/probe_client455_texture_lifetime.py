"""Observe the unchanged real engine during the full nuclear registry scenario."""
import json
from pathlib import Path
from audit_client455_item_payloads import record
from checkpoint_client455_rvp_effects import require,sha
from compare_client_binaries import WS
from probe_client455_nuclear_registry import main as scenario


def main():
    report=scenario(source_name='client455_texture_lifetime_probe.cpp',probe_name='texture-lifetime',report_name='client455-texture-lifetime-native')
    path=WS/'inventory/client455-texture-lifetime-native.json';trace=(WS/report['exe']['file']).parent/'texture-trace.json';require(trace.exists(),'Complete native texture trace')
    report.update(scope='Actual registry/world scenario with read-only own cache/table observations and lab-owned COM pins;target texture-release parity;not full world lifecycle acceptance',script_sha256=sha(Path(__file__)),scenario_script=record(WS/'scripts/probe_client455_nuclear_registry.py'),included_sources=[record(WS/'scripts/native'/x) for x in ['client455_nuclear_registry_probe.cpp','client455_texture_lifetime_trace.h']],trace=record(trace),engine_library_sha256=json.loads((WS/'inventory/client455-startup-engine-build.json').read_text())['library_sha256'])
    path.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(trace=str(trace),observations=json.loads(trace.read_text())['checks'])))


if __name__=='__main__':main()
