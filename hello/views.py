from PIL import Image
from django.shortcuts import render
from django.http import HttpResponse
from collections import Counter
import urllib, cStringIO
import numpy as np
import random
from .models import Greeting, Swatch
from scipy import spatial

# Create your views here.
def index(request):
	# return HttpResponse('Hello from Python!')
	return render(request, 'index.html')


def db(request):

	greeting = Greeting()
	greeting.save()

	greetings = Greeting.objects.all()

	return render(request, 'db.html', {'greetings': greetings})

def resize_image(URL, SIZE_RATIO):
	file = cStringIO.StringIO(urllib.urlopen(URL).read())
	with Image.open(file) as image:
		size = (image.size[0]/SIZE_RATIO, image.size[1]/SIZE_RATIO)
		cover = image.resize(size)
		return cover

def rgb_distance(swatch_tuple, rgb):
	x_diff_squard = (swatch_tuple[0][0] - rgb[0])**2
	y_diff_squard = (swatch_tuple[0][1] - rgb[1])**2
	z_diff_squard = (swatch_tuple[0][2] - rgb[2])**2
	return x_diff_squard + y_diff_squard + z_diff_squard

def get_min_swatch(swatch_tuples, rgb):
	def rgb_diff(swatch_tuple):
		return -rgb_distance(swatch_tuple, rgb)
	return max(swatch_tuples, key=rgb_diff)


def find_nearest_vector(array, value):
	idx = np.array([np.linalg.norm(x+y+z) for (x,y,z) in array-value]).argmin()
	return idx

def break_image_down_into_grid_of_swatches(image, swatch_tuples):
	image_arr = np.asarray(image)
	height = image.size[0]
	width = image.size[1]
	image_arr_swatches = [[0 for i in range(height)] for j in range(width)]

	points = np.array([[swatch[0][0], swatch[0][1], swatch[0][2]] for swatch in swatch_tuples])
	tree = spatial.KDTree(points)
	list_of_swatches = {}
	for i, row in enumerate(image_arr):
		list_of_swatches[i] = {}
		for j,col in enumerate(row):
			min_swatch = swatch_tuples[tree.query(col, k=1)[1]]
			color_tuple = min_swatch[0]
			red_hex = "{0:x}".format(int(color_tuple[0]))
			green_hex = "{0:x}".format(int(color_tuple[1]))
			blue_hex = "{0:x}".format(int(color_tuple[2]))

			hex_color = red_hex.zfill(2) + green_hex.zfill(2) + blue_hex.zfill(2)
			image_arr_swatches[i][j] = (hex_color, min_swatch[1])
	return image_arr_swatches

def get_counts_of_swatches(list_of_swatches):
	swatch_counts = Counter([swatch for swatch_list in list_of_swatches for swatch in swatch_list])
	return swatch_counts.most_common()

def allcolors(request):
	swatch_tuples = [
		(
			(
				"{0:x}".format(swatch.red).zfill(2)+"{0:x}".format(swatch.green).zfill(2)+"{0:x}".format(swatch.blue).zfill(2)
			), 
			swatch.name,
			(
				swatch.red,swatch.green,swatch.blue
			), 
		) 
		for swatch in Swatch.objects.all()
	]
	return render(request, 'allcolors.html', {'allcolors': swatch_tuples})

def masonart(request):
	URL = request.GET.get("URL", default="http://pic.1fotonin.com/data/wallpapers/60/WDF_1061456.jpg")
	SIZE_RATIO = int(request.GET.get("SIZE_RATIO",default="50"))
	LIMIT = float(request.GET.get("LIMIT",default="1"))

	swatch_tuples = [((swatch.red, swatch.green, swatch.blue), swatch.name) for swatch in Swatch.objects.all()]
	if LIMIT != 1:
		sample_indexes = random.sample(xrange(len(swatch_tuples)), int(len(swatch_tuples) * LIMIT))
		swatch_tuples = [swatch_tuples[i] for i in sample_indexes]

	image = resize_image(URL, SIZE_RATIO)
	list_of_swatches = break_image_down_into_grid_of_swatches(image, swatch_tuples)
	swatch_counts = get_counts_of_swatches(list_of_swatches)

	return render(request, 'masonart.html', {'swatches_matrix': list_of_swatches, 'swatch_counts': swatch_counts, 'original_url': URL})

