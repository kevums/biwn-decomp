"""Build a separate isolated scene backend with recovered65E0/6860 materials."""
from datetime import datetime,timezone
import hashlib,json,os,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    historical=json.loads((ROOT/'verification/scene-render-device-build.json').read_text())
    old=ROOT/'tools/libbiwn-scene-render-device.dylib';assert sha(old)==historical['library_sha256']
    source=ROOT/'projects/black-ice-white-noise/restoration';bridge=ROOT/'scripts/biwn_expanded_scene_render_device_bridge.c';library=ROOT/'tools/libbiwn-expanded-scene-render-device.dylib'
    command=[str(bridge)if value.endswith('/scripts/biwn_scene_render_device_bridge.c')else str(library)if value==str(old)else value for value in historical['command']]
    index=command.index('-lm');command[index:index]=[str(source/'biwn_gpu_material65e0.c'),str(source/'biwn_gpu_material6860.c')]
    out=ROOT/'verification/expanded-scene-render-device'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    built=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.log').write_text(built.stdout+built.stderr);assert built.returncode==0,built.stderr
    paths=[Path(value)for value in command if value.endswith(('.c','.h'))]
    # Snapshot bridge-source context in addition to direct compiler inputs.
    paths+=list((ROOT/'scripts').glob('biwn_*bridge.c'))
    report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='compiled_not_behavioral_proof',directory=str(out),command=command,library=str(library),library_sha256=sha(library),source_sha256={str(p.relative_to(ROOT)):sha(p)for p in paths},historical_device_unchanged=sha(old)==historical['library_sha256'],scope='Separate expanded isolatedgeometry backend adds existing65E0/6860 Cshaders to original57A0 drawdispatch. OriginalGPUguardand capturedgeometryreset retained. Behavioral evidence belongs to scene-render-pipeline reports, not compilation.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'verification/expanded-scene-render-device-build-current.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(directory=str(out),library_sha256=report['library_sha256'])),flush=True)
if __name__=='__main__':main()
