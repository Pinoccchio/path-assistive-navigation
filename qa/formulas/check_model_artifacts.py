"""Bounded desktop parity check. Does not change models or historical reports."""
import hashlib
import json
from pathlib import Path
import numpy as np
import onnxruntime as ort
import tensorflow as tf
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'runs/public_phase1_person_retention_candidate'
meta = json.loads((ROOT / 'apps/mobile/assets/model/model_metadata.json').read_text())
paths = {'app_tflite': ROOT / 'apps/mobile/assets/model/best_float32.tflite',
         'source_pt': ROOT / meta['source_weights'].replace('\\','/'),
         'source_onnx': ROOT / meta['source_onnx'].replace('\\','/'),
         'export_tflite': BASE / 'tflite_fp32/best_float32.tflite'}
hashes = {key: hashlib.sha256(path.read_bytes()).hexdigest() for key,path in paths.items()}
interpreter = tf.lite.Interpreter(model_path=str(paths['app_tflite']), num_threads=2)
interpreter.allocate_tensors()
inp, out = interpreter.get_input_details()[0], interpreter.get_output_details()[0]
session = ort.InferenceSession(str(paths['source_onnx']), providers=['CPUExecutionProvider'])
samples=[]
for path in sorted((ROOT/'data/processed/public_phase1_person_retention_candidate/images/test').glob('*'))[:10]:
    with Image.open(path) as image:
        array=np.asarray(image.convert('RGB').resize((512,512)),dtype=np.float32)/255
    expected=session.run(None,{session.get_inputs()[0].name: array.transpose(2,0,1)[None]})[0]
    interpreter.set_tensor(inp['index'],array[None]); interpreter.invoke()
    actual=interpreter.get_tensor(out['index']); diff=np.abs(expected-actual)
    samples.append({'image':path.name,'max_abs_error':float(diff.max()),'mean_abs_error':float(diff.mean()),'finite':bool(np.isfinite(actual).all())})
report={'review_date':'2026-11-10','scope':'Desktop raw-output export integrity only; reused development images, direct square resize. Not detection accuracy or phone preprocessing validation.',
        'hashes':hashes,'metadata_matches':hashes['app_tflite']==meta['sha256'] and hashes['source_pt']==meta['source_weights_sha256'],
        'app_matches_export':hashes['app_tflite']==hashes['export_tflite'],
        'input':{'shape':inp['shape'].tolist(),'dtype':str(inp['dtype']),'quantization':inp['quantization']},
        'output':{'shape':out['shape'].tolist(),'dtype':str(out['dtype'])},'class_names':meta['class_names'],
        'samples':samples,'sample_count':len(samples),'max_abs_error':max((x['max_abs_error'] for x in samples),default=None),
        'all_finite':bool(samples) and all(x['finite'] for x in samples)}
report['contract_checks_pass']=(report['metadata_matches'] and report['app_matches_export'] and inp['shape'].tolist()==[1,512,512,3] and out['shape'].tolist()==[1,12,5376] and inp['dtype']==np.float32 and out['dtype']==np.float32 and len(samples)==10 and report['all_finite'] and report['max_abs_error'] < .01)
report['parity_tolerance_note']='0.01 maximum absolute raw-output difference is a review smoke-check threshold, not a published accuracy guarantee.'
target=ROOT/'qa/formulas/model_validation_2026-11-10.json'
target.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ('samples','hashes')},indent=2))
if not report['contract_checks_pass']: raise SystemExit(1)
