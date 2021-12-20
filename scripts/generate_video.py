import pickle
import random
import numpy as np
import cv2

size = 600
nmix = 7

with open('cache.pkl','rb') as f:
    faces = pickle.load(f)

variants = 10

def goodangle(x):
    return abs(x['yaw'])<15 and abs(x['pitch'])<15

print("Generating videos")
for p,v in faces.items():
    gv = list(filter(lambda x: goodangle(x['pose']) and x['date']!=1,v))
    print(f" + {p} ({len(v)} faces, {len(gv)} good)",end='',flush=True)
    if len(gv)<30:
        print("..skipping")
        continue
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    vw = cv2.VideoWriter(f"out/{p}.mp4",fourcc,15,(size,size))
    gv.sort(key=lambda x: x['date'])
    for i in range(len(gv)-nmix+1):
        if nmix==1:
            res = gv[i]['img']
        else:
            ff = list(map(lambda x: x['img'],gv[i:i+nmix]))
            ff = np.array(ff).astype(np.float32)/255.0
            res = (255*ff.mean(axis=0)).astype(np.ubyte)
        vw.write(cv2.cvtColor(res,cv2.COLOR_RGB2BGR))
    vw.release()
    print("done")