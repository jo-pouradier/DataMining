import os
from PIL import Image
import numpy as np
import math
from sklearn.cluster import MiniBatchKMeans
import json
from numpyencoder import NumpyEncoder
import time
import multiprocessing as mp
import sys

starting_time = time.perf_counter()

def getExif(folder):
    data = []
    for img_path0 in os.listdir(folder):
        if img_path0[-3:] in ["jpg", "png"]:
            img_path =  folder + img_path0
            with Image.open(img_path) as img:
                width, height = img.size
                format = img.format
                try:
                    orientation = img._getexif()[274]
                except:
                    orientation = "no exif"
                data.append({"theme": folder.split('/')[2], "image": img_path0, "width": width, "height": height, "format": format, "orientation": orientation})
    return data

def getKmeans(img):
    # init
    img = Image.open(img) # open image
    if "jpg" in img.filename:
        imgfile = img.resize((int(img.size[0]/5), int(img.size[1]/5))) # resize
    else:
        imgfile = img
    numarray = np.array(imgfile.getdata(), np.uint8) # convert image to numpy array
    cluster_count = 5 # number of clusters
    clusters = MiniBatchKMeans(n_clusters=cluster_count, n_init="auto") # init kmeans
    clusters.fit(numarray) # fit kmeans
    npbins = np.arange(0, cluster_count + 1) # init bins
    histogram = np.histogram(clusters.labels_, bins=npbins) # get histogram
    #labels = numpy.unique(clusters.labels_) # get labels

    # getting colors
    color = []
    for i in range(cluster_count):
        color.append(
            "#%02x%02x%02x" % (math.ceil(clusters.cluster_centers_[i][0]),math.ceil(clusters.cluster_centers_[i][1]),math.ceil(clusters.cluster_centers_[i][2]),)
        )
    #barlist = plot.bar(labels, sorted(histogram[0], reverse=True), color=color)
    #plot.show()
    return (color)


list_of_colors = [
                (204,0,0), #red
                (204,102,0),# brown
                (204,204,0),# yellow
                (102,204,0),# lightgreen
                (0,204,0),# green
                (0,204,102),# bluegreen
                (0,204,204),# lightblue
                (0,102,204), # blue
                (0,0,204), # darkblue
                (102,0,204), # purple
                (204,0,204), # pink
                (204,0,102), # darkpink
                (255,255,255), # white
                (192,192,192), # lightgrey
                (128,128,128), # grey
                (64,64,64), # darkgrey
                (0,0,0) # black
]

color_to_name = ["red", "brown", "yellow", "lightgreen","green","bluegreen", "lightblue","blue","darkblue", "purple", "pink","darkpink", "white","lightgrey", "grey","darkgrey", "black"]

def color_hex_to_rgb(color):
    return list(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_name(color_to_name,list_of_colors ,rgb):
    return color_to_name[list_of_colors.index(tuple(rgb))]


def closest_color(colors,color_hexa):
    color = color_hex_to_rgb(color_hexa)
    colors = np.array(colors)
    color = np.array(color)
    distances = np.sqrt(np.sum((colors-color)**2,axis=1))
    index_of_smallest = np.where(distances==np.amin(distances))
    smallest_distance = colors[index_of_smallest]
    return smallest_distance 

def getDiagram(img):
    imgfile = Image.open(img)
    histogram = imgfile.histogram()
    red = histogram[0:255]
    green = histogram[256:511]
    blue = histogram[512:767]
    mapping = {"red": np.average(range(0,255),weights=red), "green": np.average(range(0,255),weights=green), "blue": np.average(range(0,255),weights=blue)}
    mapping2 = {}
    for key in mapping:
        mapping2[key] = mapping[key]/255
        if mapping2[key] < 0.33:
            mapping2[key] = 0.15
        elif mapping2[key] > 0.66:
            mapping2[key] = 0.85
        else:
            mapping2[key] = 0.5
    return mapping2


def write_data(data):
    with open('./images/ExifDatatest2MP.json', 'a+') as f:
        json.dump(data, f, indent=4, cls=NumpyEncoder)

# processing 4 folder with multiprocessing
def processingFolder(folder):
    start_time = time.perf_counter()
    # print working directory
    print(f"Working directory = {os.getcwd()}, working with {folder}")
    data = getExif(folder)
    for obj in data:
        dir = os.path.join("images", obj["theme"], obj["image"])
        colors = getKmeans(dir)
        for n, c in enumerate(colors):
            rgb =(closest_color(list_of_colors,c))[0]
            obj[f"color_{n}"] = rgb_to_name(color_to_name, list_of_colors, rgb)
        RGB = getDiagram(dir)
        for key, value in RGB.items():
            obj[key] = value
    write_data(data)
    print(f"Processing time of {folder} = {np.round(time.perf_counter() - start_time, decimals=3)}")
    return

if __name__ == "__main__":
    starting_time = time.perf_counter()
    with mp.Pool(processes=4) as p:
        p.map(processingFolder, ["./images/Exoplanet/", "./images/Moto/", "./images/Pokemon2/", "./images/Voitures/"])
    print(f"Over all processing time = {np.round(time.perf_counter() - starting_time, decimals=3)}")