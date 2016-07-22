import sys
from psychopy import visual, core, event, gui
import json
import os
from os import listdir
from os.path import isfile, join
import numpy as np

from utils import flicker


emotions = ['happy',
			'sad',
			'neutral']

def text_and_stim_keypress(win, text, stim=None):
		if stim is not None:
			if type(stim) == list:
				map(lambda x: x.draw(), stim)
			else:
				stim.draw()
		display_text = visual.TextStim(win, text=text,
										font='Helvetica', alignHoriz='center',
										alignVert='center', units='norm',
										pos=(0, 0), height=0.1,
										color=[255, 255, 255], colorSpace='rgb255',
										wrapWidth=2)
		display_text.draw()
		win.flip()
		key = event.waitKeys()
		if key[0] == 'escape':
			core.quit()
			win.flip()
		win.flip()
		return key[0]

def text(win, text):
	display_text = visual.TextStim(win, text=text,
                                       font='Helvetica', alignHoriz='center',
                                       alignVert='center', units='norm',
                                       pos=(0, 0), height=0.1,
                                       color=[255, 255, 255], colorSpace='rgb255',
                                       wrapWidth=2)
	display_text.autoDraw=True
                                      
	return display_text

def play_example(win, movie, timing):
	mov = visual.MovieStim3(win, 'movies/examples/'+movie, size=[1080,637.5],
                       flipVert=False, flipHoriz=False, loop=False)
	
	timer = core.CountdownTimer(timing)
	mov_start = core.getTime()
	flicker(win, 1)
	event.clearEvents(eventType='keyboard')
	
	while mov.status != visual.FINISHED and timer.getTime()>0:
		mov.draw()
		win.flip()

def play_movie(win, movie, timing):
	mov = visual.MovieStim3(win, 'movies/'+movie, size=[1080,637.5],
                       flipVert=False, flipHoriz=False, loop=False, noAudio=True)
	
	timer = core.CountdownTimer(timing)
	mov_start = core.getTime()
	flicker(win, 1)
	event.clearEvents(eventType='keyboard')
	
	while mov.status != visual.FINISHED and timer.getTime()>0:
		mov.draw()
		win.flip()
	
	return mov_start

def play_through_movies(win, files, timing, keymap, participant, num_movies, delay):
	num_happy = len(files['happy'])
	num_neut = len(files['neutral'])
	num_sad = len(files['sad'])
		
	options = np.random.randint(3, size=num_movies)
	
	temp = num_movies
	if num_sad<num_movies or num_happy<num_movies or num_neut<num_movies:
		num_movies = min(num_happy, num_neut, num_sad)
	
	happy_opt = np.random.choice(range(num_happy), size=num_movies, replace=False)
	neut_opt = np.random.choice(range(num_neut), size=num_movies, replace=False)
	sad_opt = np.random.choice(range(num_sad), size=num_movies, replace=False)
	
	num_movies = temp
	
	happy_count = 0
	neut_count = 0
	sad_count = 0
	trial_counter = 0
	
	for i, val in enumerate(options): 
		trial_counter += 1
		trial = {}
		
		if (happy_count == len(happy_opt)) or \
			(neut_count == len(neut_opt)) or \
			(sad_count == len(sad_opt)):
			break
			
		if val == 0:
			mov_start = play_movie(win, 'happy/'+files['happy'][happy_opt[happy_count]], timing)
			happy_count += 1
			trial['type'] = 'happy'
			trial['origin_file'] = files['happy'][happy_opt[happy_count]]
		elif val == 1:
			mov_start = play_movie(win, 'neutral/'+files['neutral'][neut_opt[neut_count]], timing)
			neut_count += 1
			trial['type'] = 'neutral'
			trial['origin_file'] = files['neutral'][neut_opt[neut_count]]
		else:
			mov_start = play_movie(win, 'sad/'+files['sad'][sad_opt[sad_count]], timing)
			sad_count += 1
			trial['type'] = 'sad'
			trial['origin_file'] = files['sad'][sad_opt[sad_count]]
		
		text_object = text(win, "                      Neutral\n\n\n\nPositive                                 Negative")
		quest_start = core.getTime()
		win.flip()
		offset = flicker(win, 4)
		key = event.waitKeys(
					maxWait=delay - offset)
				
		if key is None:
			text_object.autoDraw = False
			win.flip()
			win.flip()
			trial['response'] = 'timeout'
			trial['time_of_resp'] = 'timeout'
			trial['corr_resp'] = False
		elif 'escape' in key:
			flicker(win, 0)
			core.quit()
		else:
			text_object.autoDraw = False
			win.flip()
			win.flip()
			time_of_resp = core.getTime()
			offset = flicker(win, 16)
			trial['response'] = key[0]
			trial['time_of_resp'] = time_of_resp
			
			if trial['response'] == 'left':
				if trial['type'] == 'happy':
					trial['corr_resp'] = True
				else:
					trial['corr_resp'] = False
			elif trial['response'] == 'up':
				if trial['type'] == 'neutral':
					trial['corr_resp'] = True
				else:
					trial['corr_resp'] = False
			elif trial['response'] == 'right':
				if trial['type'] == 'sad':
					trial['corr_resp'] = True
				else:
					trial['corr_resp'] = False
			else:
				trial['response'] = 'invalid'
				trial['corr_resp'] = False
		
		trial['trial_num'] = trial_counter
		trial['mov_start'] = mov_start
		trial['quest_start'] = quest_start
		
		
		if trial['time_of_resp'] != 'timeout':
			trial['resp_time'] = time_of_resp - quest_start
				
		with open('behavioral/faces_task_'+ participant + '.json', 'a') as f:
			f.write(json.dumps(trial))
			f.write('\n')
		
		print trial_counter, trial['type'], trial['response'], trial['corr_resp']
		core.wait(delay)	

									
def save_data(day_time, start_time, participant):
	
	info = {}
	info['day_time'] = day_time
	info['start_time'] = start_time
	
	if not os.path.exists('behavioral/'):
		os.makedirs('behavioral')
	
	with open('behavioral/faces_task_'+ participant + '.json', 'a') as f:
		f.write(json.dumps(info))
		f.write('\n')
                       	
def get_settings():
    dlg = gui.Dlg(title='Choose Settings')
    dlg.addText('Biological Motion Task', color="Blue")
    dlg.addField('Subject ID:', 'practice')
    dlg.addField('Number of Movies:', 25)
    dlg.addField('Movie Timing:', 3)
    dlg.addField('Delay:', 3)
    dlg.show()
    if dlg.OK:
        return dlg.data
    else:
        sys.exit()
        
def run():	
	participant, num_movies, timing, delay = get_settings()
	
	keymap = {'left': 1, 'right': 0}
	
	# Define window
	win = visual.Window(winType='pyglet', monitor="testMonitor", units="pix", screen=1,
        	fullscr=True, colorSpace='rgb255', color=(0, 0, 0))
	win.mouseVisible = False
	
	# Instructions
	text_and_stim_keypress(win, "You are going to be watching movies of faces.\n\n" +
								'		   (Press any key to continue)')
	text_and_stim_keypress(win, "When the movie finishes playing:\n\n      -Press the LEFT arrow key if the face showed a positive emotion" +
								"\n\n      -Press the RIGHT arrow key if the face showed a negative emotion" +
								"\n\n      -Press the UP arrow key if the face showed a neutral emotion")
	text_and_stim_keypress(win, "Here are some examples...\n\n")
	
	# 2-happy, 1-sad, 0-neutral, 
	examples = [f for f in listdir('movies/examples/')
					if isfile(join('movies/examples/', f))
					if f.endswith('.mp4')]
	
	happy_text = text(win, "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nPositive")
	play_example(win, examples[2], timing)
	happy_text.autoDraw = False
	win.flip()
	win.flip()
	text_and_stim_keypress(win, "Press LEFT for positive emotion")
	core.wait(delay)
	
	sad_text = text(win, "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nNegative")
	play_example(win, examples[1], timing)
	sad_text.autoDraw = False
	win.flip()
	win.flip()
	text_and_stim_keypress(win, "Press RIGHT for negative emotion")
	core.wait(delay)
	
	neut_text = text(win, "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nNeutral")
	play_example(win, examples[0], timing)
	neut_text.autoDraw = False
	win.flip()
	win.flip()
	text_and_stim_keypress(win, "Press UP for neutral emotion")
	core.wait(delay)
	
	text_and_stim_keypress(win, "Ready?\n\n" +
								'Press any key to begin!')
	
	# Starting timers and save initial information
	globalTimer = core.Clock()
	start_time = globalTimer.getTime()
	day_time = core.getAbsTime()
	
	save_data(day_time, start_time, participant)
	
	# Wait	
	win.flip()
	core.wait(delay)
	win.flip()

	# Import movies	
	files = {}
	for num, emotion in list(enumerate(emotions)):
		files[emotion] = [f for f in listdir('movies/'+emotion) 
							if isfile(join('movies/'+emotion, f))
							if f.endswith('.mp4')]
	
	
	
	# Play movies and save data
	play_through_movies(win, files, timing, keymap, participant, num_movies, delay)
	core.wait(delay)

	# Exit		
	text_and_stim_keypress(win, "You're finished!\n\n" +
								'(Press any key to exit)')
	core.quit()
	
if __name__ == '__main__':
	run()