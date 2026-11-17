"""Run the unchanged bundled TFLite model on the existing selected demo gallery."""
import os
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'
import json, hashlib, time, io
from pathlib import Path
from collections import Counter
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import tensorflow as tf

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'output/lab4/gallery-model-results'
OUT.mkdir(parents=True,exist_ok=True)
GALLERY=ROOT/'qa/phone_test_gallery'
DATA=ROOT/'data/processed/public_phase1_person_retention_candidate'
META=json.loads((ROOT/'apps/mobile/assets/model/model_metadata.json').read_text())
MODEL=ROOT/'apps/mobile/assets/model/best_float32.tflite'
digest=hashlib.sha256(MODEL.read_bytes()).hexdigest()
assert digest==META['sha256'], 'Bundled model checksum mismatch'
NAMES=META['class_names']
engine=tf.lite.Interpreter(model_path=str(MODEL),num_threads=2)
engine.allocate_tensors()
ins=engine.get_input_details()[0]; outs=engine.get_output_details()[0]
assert list(ins['shape'])==[1,512,512,3]
assert list(outs['shape'])==[1,12,5376]

def prep(image):
    # Same floor-coordinate sampling and gray padding as the Dart frame builder.
    # JPEG RGB input bypasses camera YUV conversion and sensor rotation.
    pixels=np.asarray(image.convert('RGB'))
    height,width=pixels.shape[:2]
    scale=min(512/width,512/height)
    px=(512-width*scale)/2; py=(512-height*scale)/2
    x=np.floor((np.arange(512)-px)/scale).astype(int)
    y=np.floor((np.arange(512)-py)/scale).astype(int)
    xv=(x>=0)&(x<width); yv=(y>=0)&(y<height)
    tensor=np.full((512,512,3),114/255,dtype=np.float32)
    iy,ix=np.where(yv)[0],np.where(xv)[0]
    tensor[np.ix_(iy,ix)]=pixels[np.ix_(y[yv],x[xv])].astype(np.float32)/255
    return tensor[None],scale,px,py

def iou(a,b):
    iw=max(0,min(a[2],b[2])-max(a[0],b[0]))
    ih=max(0,min(a[3],b[3])-max(a[1],b[1]))
    intersection=iw*ih
    return intersection/(max(0,a[2]-a[0])*max(0,a[3]-a[1])+max(0,b[2]-b[0])*max(0,b[3]-b[1])-intersection+1e-6)

def detect(image):
    tensor,scale,px,py=prep(image)
    engine.set_tensor(ins['index'],tensor)
    start=time.perf_counter(); engine.invoke(); elapsed=(time.perf_counter()-start)*1000
    raw=engine.get_tensor(outs['index'])[0]
    assert np.isfinite(raw).all()
    candidates=[]
    for idx in range(raw.shape[1]):
        cls=int(np.argmax(raw[4:,idx])); score=float(raw[4+cls,idx])
        if score<=.25: continue
        x,y,w,h=map(float,raw[:4,idx])
        if not np.isfinite([x,y,w,h]).all() or w<=0 or h<=0: continue
        candidates.append({'label':NAMES[cls],'confidence':score,'model_box':[x-w/2,y-h/2,x+w/2,y+h/2]})
    candidates.sort(key=lambda x:x['confidence'],reverse=True)
    accepted=[]
    for c in candidates:
        if len(accepted)>=12: break
        if any(a['label']==c['label'] and iou(a['model_box'],c['model_box'])>.5 for a in accepted):continue
        b=c['model_box']
        box=np.clip([(b[0]-px)/(image.width*scale),(b[1]-py)/(image.height*scale),(b[2]-px)/(image.width*scale),(b[3]-py)/(image.height*scale)],0,1).tolist()
        center=(box[0]+box[2])/2
        c['box_normalized']=box
        c['direction']='left' if center<1/3 else 'ahead' if center<2/3 else 'right'
        accepted.append(c)
    return accepted,elapsed

font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',14)
def annotate(image,preds,truth,name):
    image=image.convert('RGB').copy(); d=ImageDraw.Draw(image)
    for gt in truth:
        b=gt['box_normalized']; coords=[b[0]*image.width,b[1]*image.height,b[2]*image.width,b[3]*image.height]
        d.rectangle(coords,outline='#00ddff',width=2)
    for pred in preds:
        b=pred['box_normalized']; coords=[b[0]*image.width,b[1]*image.height,b[2]*image.width,b[3]*image.height]
        d.rectangle(coords,outline='#ffdf00',width=3)
        label=f"{pred['label']} {pred['confidence']:.2f} {pred['direction']}"
        x=max(0,min(coords[0],image.width-d.textlength(label,font=font)-8));y=max(0,coords[1]-25)
        d.rectangle([x,y,x+d.textlength(label,font=font)+8,y+25],fill='black');d.text((x+4,y+2),label,font=font,fill='yellow')
    image.save(OUT/f'{name}.jpg',quality=93)

entries=json.loads((GALLERY/'manifest.json').read_text())
results=[]
for entry in entries:
    file=GALLERY/entry['image']
    source=DATA/'images/test'/f"{entry['source_id']}.jpg"
    # The gallery generator re-encodes the frozen source as JPEG quality 90.
    original=Image.open(source).convert('RGB')
    encoded=io.BytesIO(); original.save(encoded,format='JPEG',quality=90)
    assert file.read_bytes()==encoded.getvalue(),f'Gallery is not the documented quality-90 source copy: {file.name}'
    image=Image.open(file).convert('RGB')
    gt=[]
    for line in (DATA/'labels/test'/f"{entry['source_id']}.txt").read_text().splitlines():
        cls,x,y,w,h=map(float,line.split())
        gt.append({'label':NAMES[int(cls)],'box_normalized':[x-w/2,y-h/2,x+w/2,y+h/2]})
    preds,ms=detect(image)
    target_gt=[g for g in gt if g['label']==entry['label']]
    target_pred=[p for p in preds if p['label']==entry['label']]
    pairs=sorted([(iou(p['box_normalized'],g['box_normalized']),pi,gi) for pi,p in enumerate(target_pred) for gi,g in enumerate(target_gt)],reverse=True)
    used_p=set();used_g=set()
    for overlap,pi,gi in pairs:
        if overlap>=.5 and pi not in used_p and gi not in used_g:used_p.add(pi);used_g.add(gi)
    row={**entry,'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'dimensions':[image.width,image.height],
         'expected_target_boxes':len(target_gt),'detected_target_boxes':len(target_pred),'matched_target_boxes_iou_0_5':len(used_g),
         'missed_target_boxes':len(target_gt)-len(used_g),'extra_target_predictions':len(target_pred)-len(used_p),
         'target_present':bool(target_pred),'target_localized':bool(used_g),'inference_ms_desktop':ms,'detections':preds,'ground_truth':gt}
    results.append(row); annotate(image,preds,target_gt,file.stem+'_annotated')
    print(json.dumps({k:row[k] for k in ['image','label','expected_target_boxes','detected_target_boxes','matched_target_boxes_iou_0_5','inference_ms_desktop']}),flush=True)

negative=[]
for name,value in [('synthetic_black',0),('synthetic_gray',114),('synthetic_white',255)]:
    image=Image.new('RGB',(640,480),(value,value,value))
    preds,ms=detect(image);negative.append({'input':name,'detections':preds,'pass_no_objects':not preds,'inference_ms_desktop':ms})
    annotate(image,preds,[],name)
summary={'model_sha256':digest,'model_path':'apps/mobile/assets/model/best_float32.tflite','input_shape':ins['shape'].tolist(),'output_shape':outs['shape'].tolist(),
         'confidence_threshold_exclusive':.25,'same_class_nms_iou':.5,'maximum_detections':12,'matching_iou_min':.5,
         'gallery_count':len(results),'target_present_images':sum(r['target_present'] for r in results),'target_localized_images':sum(r['target_localized'] for r in results),
         'expected_target_boxes':sum(r['expected_target_boxes'] for r in results),'matched_target_boxes':sum(r['matched_target_boxes_iou_0_5'] for r in results),
         'synthetic_negatives_passed':sum(r['pass_no_objects'] for r in negative),'samples':results,'negative_controls':negative,
         'limitations':['Selected demo gallery: gallery generator favors historical successful matches for several classes; not an independent accuracy sample.',
          'JPEG RGB preprocessing uses app floor sampling and letterbox; bypasses camera YUV conversion and sensor rotation.',
          'Desktop interpreter timings are not phone latency. Ground truth reused from frozen public-data labels and not independently reannotated.',
          'No phone camera, audio, haptic or navigation-safety claim follows from this gallery inference run.']}
(OUT/'results.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print('SUMMARY',json.dumps({k:v for k,v in summary.items() if k not in ['samples','negative_controls','limitations']}),flush=True)
# Readable contact sheet of the actual model outputs, without changing source images.
sheet=Image.new('RGB',(1440,1120),'white');d=ImageDraw.Draw(sheet)
for i,row in enumerate(results):
    col=i%4;rr=i//4;x=col*360;y=rr*560
    im=Image.open(OUT/(Path(row['image']).stem+'_annotated.jpg'));im.thumbnail((344,490))
    sheet.paste(im,(x+(360-im.width)//2,y+40))
    d.text((x+8,y+5),f"{row['label']} matched {row['matched_target_boxes_iou_0_5']}/{row['expected_target_boxes']}",font=font,fill='black')
    d.text((x+8,y+535),'Yellow: predictions | Cyan: target labels',font=small,fill='black')
sheet.save(OUT/'gallery_contact_sheet.jpg',quality=95)
