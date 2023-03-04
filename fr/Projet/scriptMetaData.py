import os
from PIL import Image
import numpy as np
import math
from sklearn.cluster import MiniBatchKMeans
import json
from numpyencoder import NumpyEncoder
import time

starting_time = time.perf_counter()

dir = "images"
themes = os.listdir(dir)
data = []

for theme in themes: 
    if theme in {".DS_Store", "ExifData.json","ExifData2.json","ExifDatatest.json", "Pokemon", "ExifDatatest2.json", "Analizing_wh.ipynb"}:
        pass   
    else:
        print(theme)
        dir_test = os.path.join(dir, theme)
        for image in os.listdir(dir_test):
            if image.endswith(".jpg") or image.endswith(".png"):
                #img_path =  dir + theme + '/'+ image
                img_path = os.path.join(dir, theme, image)
                with Image.open(img_path) as img:
                    width, height = img.size
                    format = img.format
                    try:
                        orientation = img._getexif()[274]
                    except:
                        orientation = "no exif"
                    data.append({"theme": theme, "image": image, "width": width, "height": height, "format": format, "orientation": orientation})

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

length = len(data)
start_time = time.perf_counter()
for obj in data:
    index = data.index(obj)
    print(' '*100, end='\r')
    print(f"Processing time = {np.round(time.perf_counter() - start_time, decimals=3)}, image {index}/{length}: {obj['image']}", end="\r")
    dir = os.path.join("images", obj["theme"], obj["image"])
    colors = getKmeans(dir)
    for n, c in enumerate(colors):
        rgb =(closest_color(list_of_colors,c))[0]
        obj[f"color_{n}"] = rgb_to_name(color_to_name, list_of_colors, rgb)
    RGB = getDiagram(dir)
    for key, value in RGB.items():
        obj[key] = value

with open('./images/ExifDatatest2.json', 'w+') as f:
    json.dump(data, f, indent=4, cls=NumpyEncoder)

print(' '*150, end='\r')
print(f"Over all processing time = {np.round(time.perf_counter() - starting_time, decimals=3)}")