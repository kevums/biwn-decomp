"""Fuse only adapted modules at their dequantized precision; retain the other quantized weights.

No model text is generated. The resulting package remains unpromoted until
loss, LM Studio loading, and visible Chat response checks have passed.
"""
import argparse
from datetime import datetime, timezone
import fcntl
import gc
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

import mlx.core as mx
from mlx.utils import tree_flatten, tree_unflatten
from mlx_lm import load
from mlx_lm.utils import save

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('job', type=Path)
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    job = args.job.resolve()
    destination = args.destination.resolve()
    assert not destination.exists(), 'Preserve existing model packages'
    selection = json.loads((job / 'checkpoint-selection.json').read_text())
    adapter = Path(selection['selected_adapter'])
    assert digest(adapter / 'adapters.safetensors') == selection['adapter_sha256']
    adapter_config = json.loads((adapter / 'adapter_config.json').read_text())
    base = Path(adapter_config['model'])
    assert base.is_dir()
    report = {'time': datetime.now(timezone.utc).isoformat(), 'status': 'running',
              'base': str(base), 'selected_adapter': str(adapter),
              'adapter_sha256': selection['adapter_sha256'],
              'destination': str(destination), 'promotion': 'unpromoted',
              'method': 'Only adapted modules fused at dequantized precision; all other modules retain original weights and quantization.'}
    report_path = job / 'hybrid-package.json'
    def record():
        report_path.write_text(json.dumps(report, indent=2) + '\n')
    record()
    with (ROOT / 'runs/.inference.lock').open('w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        loaded = json.loads(subprocess.run([str(Path.home() / '.lmstudio/bin/lms'), 'ps', '--json'],
                            cwd=Path.home() / '.lmstudio', check=True, capture_output=True, text=True).stdout)
        assert not loaded, 'Unload native models before packaging'
        model, tokenizer, config = load(str(base), adapter_path=str(adapter), return_config=True)
        modules = [(name, module) for name, module in model.named_modules() if hasattr(module, 'fuse')]
        assert modules
        report['adapted_modules'] = []
        for name, module in modules:
            linear = module.linear
            shape = list(linear.weight.shape)
            if hasattr(linear, 'bits'):
                shape[-1] = shape[-1] * 32 // linear.bits
            elements = 1
            for dimension in shape:
                elements *= dimension
            # Conservative FP32 estimate before creating any fused matrices.
            report['adapted_modules'].append({'name': name, 'shape': shape,
                                               'fp32_upper_bound_bytes': elements * 4})
        report['adapted_fp32_upper_bound_bytes'] = sum(row['fp32_upper_bound_bytes'] for row in report['adapted_modules'])
        assert report['adapted_fp32_upper_bound_bytes'] < 16 * 1024**3, 'Hybrid expansion exceeds lab budget'
        record()
        print('Adapted modules:', len(modules), 'FP32 upper bound:', report['adapted_fp32_upper_bound_bytes'], flush=True)
        for name, module in modules:
            fused = module.fuse(dequantize=True)
            mx.eval(fused.parameters())
            assert not hasattr(fused, 'bits')
            model.update_modules(tree_unflatten([(name, fused)]))
            # The MLX loader supports explicit per-module False predicates.
            config['quantization'][name] = False
        del module, fused, linear, modules
        gc.collect()
        mx.clear_cache()
        report['weight_bytes'] = sum(value.nbytes for _, value in tree_flatten(model.parameters()))
        assert report['weight_bytes'] < 36 * 1024**3, 'Hybrid weights exceed lab budget'
        report['peak_metal_bytes'] = mx.get_peak_memory()
        record()
        save(destination, base, model, tokenizer, config, donate_model=True)
        if (base / 'chat_template.jinja').exists() and not (destination / 'chat_template.jinja').exists():
            shutil.copy2(base / 'chat_template.jinja', destination / 'chat_template.jinja')
        report.update(status='packaged_unpromoted',
                      model_files_sha256={path.name: digest(path) for path in sorted(destination.iterdir()) if path.is_file()},
                      completed_at=datetime.now(timezone.utc).isoformat())
        record()
        training_result = json.loads((job / 'training-result.json').read_text())
        report_name = ('advertising-pilot-hybrid-package.json'
                       if training_result['domain'] == 'advertising'
                       else 'cpu-remediation-hybrid-package.json')
        (ROOT / 'verification' / report_name).write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps({'status': report['status'], 'weight_bytes': report['weight_bytes'], 'destination': str(destination)}), flush=True)


if __name__ == '__main__':
    main()
