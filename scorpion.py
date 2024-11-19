#!/bin/env python3

# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    scorpion.py                                        :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: frcharbo <frcharbo@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2024/11/19 23:00:00 by frcharbo          #+#    #+#              #
#    Updated: 2024/11/19 23:02:31 by frcharbo         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import sys
from PIL import Image, ExifTags
from PIL.ExifTags import TAGS

def display_basic_attributes(file):
    width, height = file.size
    mode = file.mode
    format_ = file.format
    print(f"Width: {width}")
    print(f"Height: {height}")
    print(f"Color Mode: {mode}")
    print(f"Format: {format_}")

def display_exif_attributes(file):
    exifs = file.getexif()
    if exifs is None: #certain formats like some pngs dont acc support metadata
        print('No exif data for this image')
        return
    if len(exifs) == 0: #vs supported formats but simply none there or its been stripped
        print('No exif data for this image')
        return
    for id_tag in exifs:
        tag = TAGS.get(id_tag, id_tag)
        data = exifs.get(id_tag)
        if isinstance(data, bytes):
            try:
                data = data.decode()
            except:
                data = "Non readable data"
        print(f"{tag} : {data}")

def scorpion(path):
    print(path + ":")
    try:
        file = Image.open(path)
    except:
        print('Error: Unable to open ', path)
        return
    display_basic_attributes(file)
    display_exif_attributes(file)
    print('')

for pos in range(len(sys.argv)):
    if pos == 0:
        continue
    scorpion(sys.argv[pos])