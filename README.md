# Cognitive Art 
## Creating Cognitive Art from your Family Photo Archive

This repository contains code that allows you to generate [cognitive portraits](https://soshnikov.com/art/peopleblending) for people from your family photo album, as well as grow-up videos like this one:

<a href="https://www.youtube.com/watch?v=ZcGrFB9idiY" style="text-align: center"><img src="https://img.youtube.com/vi/ZcGrFB9idiY/0.jpg"/></a>

> You are free to make any use of the code in this repository, provided you attribute the original idea of [cognitive portrait](https://soshnikov.com/art/peopleblending) to [Dmitry Soshnikov](https://soshnikov.com).

## Step 0: Setting Up

You probably want to start from cloning this GitHub repository to your own computer, and making sure you have decent Python environment installed. 

Copy `config_template.yaml` file into `config.yaml` - you will specify different configuration options there. Start by providing a path to your family photo archive in **Directories -> Source**.

To install all required libraries into your Python environment, run
```bash
pip install -r requirements.txt
```  
(You may want to create a separate virtual environment for that).
## Step 1: Creating Cognitive Service

We will be using [Azure Face API](https://docs.microsoft.com/azure/cognitive-services/face/?WT.mc_id=academic-35500-dmitryso) to do the following:
* Identify faces of different people in your photo archive
* Extract Facial Landmarks from the photographs

> If you do not have an access to [Microsoft Azure](http://azure.microsoft.com/?WT.mc_id=academic-35500-dmitryso), feel free to apply for [Azure for Students](https://azure.microsoft.com/free/students/?WT.mc_id=academic-35500-dmitryso) or [GitHub Student Developer Pack](https://education.github.com/pack) if you are a student, or [Azure Free Trial](https://azure.microsoft.com/free/?WT.mc_id=academic-35500-dmitryso).

Once you do this, [create Face API cloud resource](https://portal.azure.com/#create/Microsoft.CognitiveServicesFace/?WT.mc_id=academic-35500-dmitryso), grab **endpoint** and **key**, and put them into `config.yaml`.

> **Note**: Create payed version of the resource, because the free version has the limitation of 20 calls per minute, and you may run out of this limitation. Please check Face API pricing before that. At the time of this writing, 

## Step 2: Creating Facial Database and training Face API

Start by creating a database of photographs of people that you want to recognize automatically on the photographs. Create a directory somewhere, and put 6-15 photographs of each person into a subdirectory nick-named after that person (preferably no spaces in directory names). The more diverse photographs you use - the better recognition results would be. Put the name of the directory with faces into `config.yaml` (**Directories -> Train**).

Once you do that, train Face API to recognize all those faces by calling:

```bash
python scripts/trainfaces.py
```

This will also create `people.map` text file that contains mapping between people's nicknames and their corresponding GUIDs.
## Step 3: Process the whole Photo Archive

The main script that will traverse your entire photo archive is called by
```bash
python scripts/process.py
```

This process is likely to take a long time. It will store the results of processing into `db` directory, so in case there are any interruptions - all processed images will be skipped. Also, to speed things up, you may specify the name of the directory at which to restart processing by changing `restart_at` variable at the top of the script from `None` to the directory name.

## Step 4: Transforming all images

To transform all images and prepare them to generate portraits, call
```bash
python scripts/prepare.py
```

In this script, the variable `size` defined at the top specifies target size of all images - change it if you like.

This process will traverse all photo archive, and group all faces from recognized people into buckets, also resizing photographs and aligning faces in the right way. The result of this script is saved into `cache.pkl` file.

> **Note**: Because `cache.pkl` contains the resized version of each image in uncompressed form, this file can take quite a bit of disk space. Make sure you have it. Also, in case you have too many photos, they might not all fit into memory during processing - in which case you may need to change the script logic to avoid in-memory processing of all photos.

## Step 5: Generating Portraits

Finally, to generate cognitive portraits for all people, call
```bash
python scripts/generate.py
```
This will create a number of random portraits for each person in `out` subdirectory, named under person's GUID.

## Step 6: Generate Videos

If you have sufficiently large number of photos for each person, you can also generate "growup" videos. To do this, call
```bash
python scripts/generate_video.py
```

You may change the style of video by changing `nmix` variable at the top of the script - it indicates how many frames are mixed together each time to create cognitive portrait effect. By setting `nmix` to `1` you will have original images in the video.

## Step 7: Enjoy!

If you like this repo, please send me your feedback! You can find out my contact info [at my website](https://soshnikov.com).
