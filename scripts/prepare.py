import shelve
import cv2
import tqdm
import numpy as np
import pickle
import os

size = 600
dest_dir = None # set to a directory to put all normalized images there
unknown_faces_name = None # set to a string to group all unknown faces under this name

target_triangle = [(x/300*size,y/300*size) for (x,y) in [(130,120),(170,120),(150,160)]]

def transform(image,f):
    mc_x = (f['mouth_left']['x']+f['mouth_right']['x'])/2.0
    mc_y = (f['mouth_left']['y'] + f['mouth_right']['y']) / 2.0
    tr = cv2.getAffineTransform(np.float32([(f['pupil_left']['x'],f['pupil_left']['y']),(f['pupil_right']['x'],f['pupil_right']['y']),(mc_x,mc_y)]),
                                np.float32(target_triangle))
    return cv2.warpAffine(image,tr,(size,size))

print("Processing all pictures")

db = shelve.open('db/photos.db')
good = { k:v for k,v in db.items() if v['status'] == 'ok' }
faces = {}

for k,v in tqdm.tqdm(good.items()):
    img = cv2.imread(k)
    if img is None:
        continue
    img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
    for f in v['face_info']:
        if f['person']=='':
            if unknown_faces_name:
                f['person'] = unknown_faces_name
            else:
                continue
        if f['person'] not in faces.keys():
            faces[f['person']] = []
        faces[f['person']].append({ "date" : v['date'], "img" : transform(img,f['face_landmarks']), "pose" : f['face_attributes']['head_pose'] })

print("Saving result")

with open('cache.pkl','wb') as f:
    pickle.dump(faces,f)

if dest_dir:
    for k,v in faces.items():
        os.makedirs(os.path.join(dest_dir,k),exist_ok=True)
        for i,im in enumerate(v):
            img = cv2.cvtColor(im['img'],cv2.COLOR_BGR2RGB)
            cv2.imwrite(os.path.join(dest_dir,k,str(i)+'.jpg'),img)
