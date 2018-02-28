#!/usr/bin/env python

import os
import sys
import subprocess
import boto3
import botocore
import fnmatch
import time 
import ntpath

from PIL import Image

if len(sys.argv) > 1:
    wait_time = int(sys.argv[1])
else:
    wait_time = 60 # seconds
num_segs = 3
threshold = 0.14
if len(sys.argv) > 2:
    initial_max_im_num = int(sys.argv[2])
else:
    initial_max_im_num = -1
image_name_pattern = 'image{}{}.jpg'
image_save_folder = '/home/ec2-user/parking-counter/ec2/'

s3 = boto3.resource('s3')
bucket = s3.Bucket('parkingcounter')

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('parkingcounter')

def count_cars(image_path):
    os.chdir('/home/ec2-user/darknet/')
    bash_command = './darknet detect cfg/yolo.cfg yolo.weights {} -thresh {}'.format(image_path, threshold)
    process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()

    data = open('predictions.png','rb')
    bucket.put_object(ACL='public-read', Key=ntpath.basename(image_path).split('.')[0] + '.png', Body=data)
    count = output.count('\ncar: ')
    print('counted {} cars in {}'.format(count, image_path))
    return count

def run_on(im_num):
    image_name = image_name_pattern.format(im_num, '')
    print('running on {}'.format(image_name))
    try:
        bucket.download_file(image_name, image_save_folder + image_name)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == '404':
            print('the object does not exist.')
            return
        else:
            raise

    img = Image.open(image_save_folder + image_name)
    width = img.size[0]
    height = img.size[1]
    first_t = width/3
    second_t = (width/3) * 2
    img_1 = img.crop((0, 0, first_t, height))
    img_2 = img.crop((first_t, 0, second_t, height))
    img_3 = img.crop((second_t, 0, width, height))
    one = image_name_pattern.format(im_num, "_1")
    two = image_name_pattern.format(im_num, "_2")
    three = image_name_pattern.format(im_num, "_3")
    img_1.save(image_save_folder + one)
    img_2.save(image_save_folder + two)
    img_3.save(image_save_folder + three)
    total_cars = count_cars(image_save_folder + one) + count_cars(image_save_folder + two) + count_cars(image_save_folder + three)
    print('counted {} cars in {}'.format(total_cars, image_name))
    response = table.scan()
    item = response['Items']
    print(item)
    nextNum = len(item)+1
    table.put_item(
        Item={
            'index': nextNum,
            'image_name': image_name,
            'car_count': total_cars,
        }
    )
    
    os.remove(image_save_folder + one)
    os.remove(image_save_folder + two)
    os.remove(image_save_folder + three)
    os.remove(image_save_folder + image_name)

def run_on_more_recent(max_im_num):
    old_max = max_im_num
    key_names = []
    for key in bucket.objects.all():
        key_names.append(key.key)

    filtered = fnmatch.filter(key_names, image_name_pattern.format('*', ''))

    for key_name in filtered:
        im_num = int(filter(str.isdigit, key_name.encode('utf-8')))
        if im_num > max_im_num:
            max_im_num = im_num
    if max_im_num > old_max:
        run_on(max_im_num)
    return max_im_num


max_im_num = initial_max_im_num

while True:
    start_time = time.time()
    max_im_num = run_on_more_recent(max_im_num)
    cur_wait_time = wait_time - (time.time() - start_time)
    print('waiting {}s'.format(cur_wait_time))
    if cur_wait_time > 0:
        sys.stdout.write('sleepy time')
        sys.stdout.flush()
        for x in range(10):
            time.sleep(cur_wait_time/10)
            sys.stdout.write('.')
            sys.stdout.flush()
    else:
        print('no sleepy time for you!')

print(count_cars('/home/ec2-user/output/picture6.JPG'))

