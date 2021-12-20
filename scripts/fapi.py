import yaml
import os
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.face.models import Person, FaceAttributeType as FAT

with open('config.yaml') as f: 
    conf = yaml.load(f,Loader=yaml.loader.SafeLoader)

def get_conf():
    return conf

def get_face_client():
    return FaceClient(conf['FaceApi']['Endpoint'], CognitiveServicesCredentials(conf['FaceApi']['Key']))

def all_attributes():
    return [FAT.emotion, FAT.exposure, FAT.accessories, FAT.facial_hair, FAT.age, FAT.gender, FAT.blur, FAT.glasses, FAT.head_pose, FAT.makeup, FAT.occlusion, FAT.smile]
