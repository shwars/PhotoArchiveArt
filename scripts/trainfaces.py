import fapi
import os
from azure.cognitiveservices.vision.face.models import TrainingStatusType
import time

src_dir = fapi.get_conf()['Directories']['Train']
cli = fapi.get_face_client()
pg_id = "shwarspeople"
need_delete = True

# More documentation on the used SDK features is available at
# https://docs.microsoft.com/azure/cognitive-services/face/quickstarts/client-libraries?tabs=visual-studio&pivots=programming-language-python#identify-a-face

people = {}

if need_delete:
    print(" + Deleting person group")    
    cli.person_group.delete(pg_id)

print(" + Creating person group")
cli.person_group.create(pg_id,"My family album person group")

for p in os.scandir(src_dir):
    if not p.is_dir():
        continue
    print(f" + Creating person {p.name}")
    pers = cli.person_group_person.create(pg_id,p.name)
    people[p.name] = pers
    for f in os.scandir(os.path.join(src_dir,p.name)):
        with open(os.path.join(src_dir,p.name,f.name),'rb') as s:
            try:
                cli.person_group_person.add_face_from_stream(pg_id,pers.person_id,s)
            except:
                print(f"   > Error in file {f.name}")

print(" + Writing id mapping")
with open('people.map','w') as f:
    for k,v in people.items():
        f.write(f"{k} {v.person_id}\n")

print(" + Training",end='',flush=True)
cli.person_group.train(pg_id)
while True:
    stat = cli.person_group.get_training_status(pg_id)
    if stat.status == TrainingStatusType.succeeded:
        print("done")
        break
    if stat.status == TrainingStatusType.failed:
        print("failed")
        print(" + Deleting person group")
        cli.person_group.delete(pg_id)
        break
    time.sleep(5)
