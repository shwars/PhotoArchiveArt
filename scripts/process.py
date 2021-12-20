# Process file archive

import fapi
import shelve
import os
import dlib
import random
from PIL import Image
import time, datetime
import numpy as np
import io

# You may specify the directory at which to restart processing
restart_at = None # "2021-Winter"

src_dir = fapi.get_conf()['Directories']['Source']
rndskip = float(fapi.get_conf()['Params']['RandomSkip'])
cli = fapi.get_face_client()
pg_id = "shwarspeople"

all_attributes = ['accessories','age','blur','emotion','exposure','facialhair','gender','glasses','hair','headpose','makeup','noise','occlusion','qualityforrecognition','smile']

total_calls = 0
total = 0
total_with_face = 0
total_faces = 0
ppl_count = {}

def facesize_x(f):
    return f.right()-f.left()

# load the image
# return a tuple of np-array and exif date
def imload(fn):
    im = None
    try:
        im = Image.open(fn)
        dt = im._getexif()[36867]
        st = time.strptime(dt,"%Y:%m:%d %H:%M:%S")
        dt = datetime.datetime(*st[:6])
    except:
        dt = datetime.MINYEAR
    return im, dt

db = shelve.open('db/photos.db')

detector = dlib.get_frontal_face_detector()

queue = [src_dir]

while len(queue)>0:
    cd = queue.pop(0)
    for f in os.scandir(os.path.join(src_dir,cd)):
        fn = os.path.join(src_dir,cd,f.name)
        if f.is_dir():
            queue.append(fn)
            continue
        if restart_at:
            if restart_at in fn:
                restart_at = None
            else:
                continue
        if not f.is_file():
            continue
        if fn in db.keys():
            print(f"Skipping: {fn}")
            continue
        if random.uniform(0,1)<rndskip:
            continue
        total+=1
        if f.stat().st_size>10*1024*1024:
            print(f"File too big: {fn}...")
            db[fn] = { "status" : "too_big" }
            continue
        if not(f.name.lower().endswith(".png") or f.name.lower().endswith(".jpg") or f.name.lower().endswith('.jpeg')):
            continue 
        print(f"Processing: {fn}...",end='',flush=True)
        im,dt = imload(fn)
        if im is None:
            continue
        try:
            img = np.array(im)
            fcs = detector(img,0)
        except:
            fcs = []
        print(f"{len(fcs)} faces")
        if len(fcs)==0:
            db[fn] = { "status" : "nofaces", "faces" : fcs, "date" : dt }
            continue
        if max([facesize_x(x) for x in fcs])/im.size[0]<0.07:
            db[fn] = { "status" : "smallfaces", "faces" : fcs, "date" : dt }
            print("small")
            continue
        total_with_face+=1
        if im.size[0] > 3000: # image size too large
            scale_factor = 2
            im = im.resize((im.size[0]//scale_factor,im.size[1]//scale_factor),Image.LANCZOS)
        else:
            scale_factor = 1
        buf = io.BytesIO()
        im.save(buf,format='JPEG')
        buf.seek(0)
        res = cli.face.detect_with_stream(buf,return_face_id=True,return_face_landmarks=True,return_face_attributes=fapi.all_attributes())
        total_faces+=len(res)
        ids = [f.face_id for f in res]
        fres = [ f.as_dict() for f in res ]
        if scale_factor>1:
            for i,f in enumerate(fres):
                for k,v in f['face_rectangle'].items():
                    fres[i]['face_rectangle'][k] = v*scale_factor
                for k,v in f['face_landmarks'].items():
                    fres[i]['face_landmarks'][k]['x'] = v['x']*scale_factor
                    fres[i]['face_landmarks'][k]['y'] = v['y']*scale_factor
        resid = [] if ids==[] else cli.face.identify(ids[:10],pg_id)
        idmap = { x.face_id : '' if len(x.candidates)<1 else x.candidates[0].person_id for x in resid }
        for i,f in enumerate(fres):
            fid = idmap.get(f['face_id'],'')
            fres[i]['person'] = fid
            if fid!="":
                ppl_count[fid] = ppl_count.get(fid,0)+1
        db[fn] = { "status" : "ok", "faces" : fcs, "date" : dt, "face_info" : fres }
        total_calls+=2        
    db.sync()
    print("-------- STATISTICS -------")
    print(f" + Files processed: {total}, detailed: {total_with_face}, faces: {total_faces}")
    print(f" + Total calls: {total_calls}, cost: ${total_calls/1000*2.5}")
    for k,v in ppl_count.items():
        print(f" > {k} -> {v}")
