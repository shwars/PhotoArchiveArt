import pickle
import random
import numpy as np
import cv2

with open('cache.pkl','rb') as f:
    faces = pickle.load(f)

variants = 10

def goodangle(x):
    return abs(x['yaw'])<15 and abs(x['pitch'])<15

print("Generating images")
for p,v in faces.items():
    gv = list(filter(lambda x: goodangle(x['pose']),v))
    print(f" + {p} ({len(v)} faces, {len(gv)} good)")
    for n in [5,10,15,20,25,50,100]:
        if n>len(gv):
            break
        for i in range(variants):
            ff = list(map(lambda x: x['img'],random.sample(gv,n)))
            ff = np.array(ff).astype(np.float32)/255.0
            res = (255*ff.mean(axis=0)).astype(np.ubyte)
            cv2.imwrite(f"out/{p}_{n}_{i}.jpg",cv2.cvtColor(res,cv2.COLOR_RGB2BGR))
