# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    spider.py                                          :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: frcharbo <frcharbo@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2024/11/18 14:15:17 by frcharbo          #+#    #+#              #
#    Updated: 2024/11/19 19:25:59 by frcharbo         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import os
import signal
import argparse
import requests
from urllib.parse import urljoin, urlparse
import urllib.request
import threading
from bs4 import BeautifulSoup

img_downloaded = {}
checked_urls = set()

def sig_handler(arg_1, arg_2):
    print('SIGINT received, aborting the program')
    exit(1)

def is_valid_url(url):
    parsed = urlparse(url)
    return bool (parsed.netloc) and bool(parsed.scheme)

def is_valid_img(img_r):
    valid_mime_types = ["image/jpg", "image/jpeg", "image/png", "image/bmp", "image/gif"]
    content_type = img_r.headers.get('content-type')
    # print(f"Content-Type: {content_type}")  # Debugging line
    if content_type in valid_mime_types:
        return (True)
    return (False)

def get_all_img_src(images, url):
    img_src = []
    for image in images:
        src = image.get('src')
        img_src.append(requests.compat.urljoin(url, src))
    return (img_src)

def download_image(img_url, save_dir):

    try:
        img_head = requests.head(img_url)
        if not is_valid_img(img_head):
            # print(f"Invalid image type for {img_url}")
            return
        img_data = requests.get(img_url).content
        if img_head.status_code != 200:
            print("error connecting to url")
        img_downloaded[img_url] = True
        print(img_url)
        img_name = os.path.basename(img_url)
        img_path = os.path.join(save_dir, img_name)

        with open(img_path, 'wb') as f:
            f.write(img_data)
        print(f"Image saved to {img_path}")
    except Exception as e:
        print(f"Error downloading {img_url}: {e}")

def single_img(url, save_dir):
    response_head = requests.head(url, allow_redirects=True)
    if response_head.status_code == 200 and is_valid_img(response_head):
        print(f"Original URL is an image. Downloading: {url}")
        download_image(url, save_dir)
        return  # Stop further processing

def spider(url, save_dir, depth):

    try:
        single_img(url, save_dir)
        if depth == 0:
            return
        if url in checked_urls:
            return
        checked_urls.add(url)
        response = requests.get(url)
        if response.status_code != 200:
            print(f"failed to retrieve URL {url} Error code {response.status_code}")
            return
        soup = BeautifulSoup(response.text, 'html.parser')
        imgs = soup.find_all('img')
        img_src = get_all_img_src(imgs, url)
        for img in img_src:
            if img not in img_downloaded:
                download_image(img, save_dir)
        links = soup.find_all('a')
        for link in links:
            href = link.get('href')
            if href:
                if href.startswith("/"):
                    href = urljoin(url, href)
                if not href.startswith("#"):
                    if urlparse(href).netloc == urlparse(url).netloc:
                        spider(href, save_dir, depth)
    except Exception as e:
        print(f"Error fetching images from {url}: {e}")       

if __name__ == "__main__":

    signal.signal(signal.SIGINT, sig_handler)
    parser = argparse.ArgumentParser(description="Image spider")
    parser.add_argument("url", help="URL to scrape")
    parser.add_argument("-r", "--recursive", action="store_true", help="Recursive image download")
    parser.add_argument("-l", "--level", type=int, help="Maximum recursive depth level")
    parser.add_argument("-p", "--path", default="./data/", help="Path where images will be saved")
    args = parser.parse_args()
    if not os.path.isdir(args.path):
        os.makedirs(args.path)
    if args.recursive:
        args.level = args.level if args.level is not None else 5
    else:
        args.level = 0
    path = args.path
    input_without_slash = args.url
    if str(input_without_slash).endswith("/"):
        input_without_slash = args.url.rstrip("/")
    if not str(path).endswith("/"):
        path += "/"
    spider(args.url, path, args.level)
