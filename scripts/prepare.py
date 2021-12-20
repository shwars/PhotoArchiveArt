import shelve
import cv2
import tqdm
import numpy as np
import pickle

size = 600

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
        if f['person']=='': continue
        if f['person'] not in faces.keys():
            faces[f['person']] = []
        faces[f['person']].append({ "date" : v['date'], "img" : transform(img,f['face_landmarks']), "pose" : f['face_attributes']['head_pose'] })

print("Saving result")

with open('cache.pkl','wb') as f:
    pickle.dump(faces,f)
