#!/usr/bin/env python

import os
import sys
import boto3
from picamera import PiCamera
from time import sleep
from PIL import Image

save_folder = './output/'
save_file_pattern = 'image{}.jpg'
numPicSegments = 3

if len(sys.argv) > 1:
    wait_time = int(sys.argv[1])
else:
    wait_time = 120 # seconds
bucket_name = 'parkingcounter'

camera = PiCamera()
camera.rotation = 180
s3 = boto3.resource('s3')
if len(sys.argv) > 2:
    i = int(sys.argv[2])
else:
    i = 0

while True:
    save_file = save_file_pattern.format(i)

    print('taking picture {}'.format(i))
    camera.start_preview(alpha=200)
    sleep(5)
    camera.capture(save_folder + save_file)
    camera.stop_preview()
    print('took picture')
    print('cropping picture')
    img = Image.open(save_folder + save_file)
    width = img.size[0]
    height = img.size[1]
    img2 = img.crop((0, 380, width, height))
    img = img2
    img.save(save_folder + save_file)
    print('uploading picture')
    data = open(save_folder + save_file, 'rb')
    s3.Bucket(bucket_name).put_object(ACL='public-read', Key=save_file, Body=data)
    print('uploaded picture\n')
    
    os.remove(save_folder + save_file)
    
    sys.stdout.write('waiting')
    sys.stdout.flush()
    for x in range(10):
        sleep(wait_time/10)
        sys.stdout.write('.')
        sys.stdout.flush()
    i += 1
    print('\n')

