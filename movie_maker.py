import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("SVG")
from matplotlib.backends.backend_svg import FigureCanvasSVG as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.animation as animation

import scipy.io as sio
from scipy.signal import savgol_filter
import os
import sys

import argparse

# Required:
# 	- Change the emotions variable in load_mat to match the MATLAB file that it comes from

emotions = {1: 'angry',
			2: 'disgust',
			3: 'happy',
			4: 'sad',
			5: 'neutral'}
			
def load_mat(filename):
	mat = sio.loadmat(filename)
	landmarks = mat['landmarks']
	emots = mat['emots_intraface']
	# 'emots' in vid1/2 files and 'emots_intraface' or 'emots_jh' in rand_001/
	landmarks = pd.DataFrame(landmarks)
	
	return landmarks, emots
	
def rle(emots):
        """ run length encoding. 
            returns: tuple (runlengths, startpositions, values) """
        ia = np.array(emots[0])                  # force numpy
        n = len(ia)
        if n == 0: 
            return (None, None, None)
        else:
            y = np.array(ia[1:] != ia[:-1])     # pairwise unequal (string safe), finds all switch points (array of bool)
            i = np.append(np.where(y), n - 1)   # must include last element posi, gets position of all switch points + final position
            z = np.diff(np.append(-1, i))       # run lengths, distance between each of the switch points
            p = np.cumsum(np.append(0, z))[:-1] # positions, start positions of runs (instead of switch points), summing z gives len(ia)
            return (z, p, ia[i])

# segments = (run length, startpositions, values) of emotions

def find_long_segments(segments, target_length, neut_len):
	long = []
	for i in range(len(segments[0])):
		
		# Is segment of video long enough?
		
		if (segments[0][i] > target_length):
			long.append((segments[0][i], segments[1][i], segments[2][i]))
			
	return long

def setup_movie_writer():
	FFMpegWriter = animation.writers['ffmpeg']
	writer = FFMpegWriter(fps=15)
	
	return writer

def filter_landmarks(landmarks):
	filtered_data = landmarks.copy()
	for i in range(len(landmarks)):
		filtered_data.iloc[i] = savgol_filter(landmarks.iloc[i], 11, 2)
	return filtered_data
	
def make_emotion_movie(landmarks, emots, filename, emotion_name, emotion_num, coords, writer):
    fig = Figure()
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(111)
    fig.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=None, hspace=None)

    fig.gca().invert_yaxis()
    
    filename = os.path.basename(filename)
    filename = filename.strip('.mat')
    newpath = 'movies/'+emotion_name
    
    if not os.path.exists(newpath):
    	os.makedirs(newpath)
    
    name = filename+'_'+emotion_name+emotion_num+'.mp4'
    print name

    with writer.saving(fig, newpath+'/'+name, 300):
        for i in range(coords[1], coords[1]+coords[0]): #coords = (length, start, value)
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_axis_bgcolor('black')
            ax.scatter(landmarks[i][0:48], landmarks[i][49:97], color='white')
            writer.grab_frame()
            ax.cla()
	
def make_movies(landmarks, emots, long, writer, filename):
	counters = np.ones(5) # angry, disgust, happy, sad, neutral
	
	for i in range(len(long)):
		if long[i][2] in emotions.keys():
			emotion = long[i][2]
			emotion_name = emotions[emotion]
			emotion_num = '_' + str(int(counters[emotion-1]))
			counters[emotion-1] += 1
			make_emotion_movie(landmarks, emots, filename, emotion_name, emotion_num, long[i], writer)
		else:
			raise Error('Something is wrong with the data. :-/')

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description = "Make movie-emotion files from .mat files")
	parser.add_argument('files', nargs='+',
						help="Files from which to produce movies"
						)
	parser.add_argument('-tl', '--target_length', dest='target', type=int, default=30, 
						help="Target length for emotion frames cutoff"
						)
	parser.add_argument('-n', '--neutral_length', dest='neut_len', type=int, default=0, 
						help="Length of neutral before emotion"
						)

	args = parser.parse_args()
	
	for file in args.files:
		print file
		#if args.files.index(file) < args.files.index('rand_001/00120.mat'):
		#	continue
		
		landmarks, emots = load_mat(file)
		segments = rle(emots)
		
		if type(segments[0]) == type(None):
			continue
		
		long = find_long_segments(segments, args.target, args.neut_len)
		if not any(long):
			continue
		
		writer = setup_movie_writer()
		filtered_data = filter_landmarks(landmarks)
		make_movies(filtered_data, emots, long, writer, file)

'''
# Non-working version of finding neutral segments preceding video
def find_long_segments(segments, target_length, neut_len):
	long = []
	for i in range(len(segments[0])):
		
		# Is segment of video long enough?
		# And preceded by X seconds of neutral video? (Can comment out to just find emotion videos)
		# Neut_len/fps (usually 15) is seconds of neutral video preceding
		#if i < neut_len:
		#	continue
		
		#neutral_amount = 0.
		#for val in segments[2][i-neut_len:i]:
		#	if val == 5.0:
		#		neutral_amount += 1
		
		if (segments[0][i] > target_length): # and (neutral_amount/neut_len >= 0.5):
			long.append((segments[0][i], segments[1][i], segments[2][i]))
	
	# (np.array_equal(segments[2][i-neut_len:i], np.full(neut_len, 5.))):
	# Need to remove neut_len if commenting out preceding neutral video
	# long.append((segments[0][i] + neut_len, segments[1][i-neut_len], segments[2][i]))	
	
	return long
'''