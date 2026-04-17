# in this experiment, we will use the blindspot project framework to place stimuli
# and test the HV illusion directly

# the reference dot pair spanning the blind spot will have a distance of the longest blindspot axis + 3 or 4 dva
# we want the comparison pair above the blind spot, but it's centre removed from the blind spot such
# that orientation can be anything without getting into the blind spot, or overlapping with the other pair

# the distance between the dots in the comparison pair will be adjusted in each trial and given a random distance offset in some margin
# in the first version, the reference pair will always be horionztal
# the comparison pair will either be rotated 45 degrees (in either direction) or be horizontal
# both dot pairs will either be presented only to the blind spot eye, or both

# we run the task twice, once for each hemifield



import psychopy
from psychopy import core, visual, gui, data, event
from psychopy.tools.coordinatetools import pol2cart, cart2pol
import numpy as np
import random, datetime, os
from glob import glob
from itertools import compress

from psychopy.hardware import keyboard
from pyglet.window import key


import sys, os
sys.path.append(os.path.join('..', 'EyeTracking'))
from EyeTracking import localizeSetup, EyeTracker

######
#### Initialize experiment
######

def doHVperceptionTask(ID=None, hemifield=None, location=None):

    ## files
    # expInfo = {'ID':'test', 'hemifield':['left','right']}
    # dlg = gui.DlgFromDict(expInfo, title='Infos', screen=0)
    # ID = expInfo['ID'].lower()
    # hemifield = expInfo['hemifield']
    expInfo = {}
    askQuestions = False
    if ID == None:
        expInfo['ID'] = ''
        askQuestions = True
    if hemifield == None:
        expInfo['hemifield'] = ['left','right']
        askQuestions = True
    # expInfo = {'ID':'test', 'hemifield':['left','right']}
    if askQuestions:
        dlg = gui.DlgFromDict(expInfo, title='Infos', screen=0)

    if ID == None:
        ID = expInfo['ID'].lower()
    if hemifield == None:
        hemifield = expInfo['hemifield']

    # need to know which eye-tracker to use:
    if location == None:
        # hacky, but true for now:
        if os.sys.platform == 'linux':
            location = 'toronto'
        else:
            location = 'glasgow'


    random.seed(ID+'HVperception'+hemifield)

    trackEyes = [True, True]

    main_path = 'data/perception_v2/'
    data_path = main_path
    eyetracking_path = main_path + 'eyetracking/' + ID + '/'

    # should already be there because of calibration tasks
    os.makedirs(data_path, exist_ok=True)
    os.makedirs(eyetracking_path, exist_ok=True)


    # create output file:
    x = 1
    # filename = '_dist_' + ('LH' if hemifield == 'left' else 'RH') + '_' + ID + '_'
    filename = ID + '_HVpercept_' + ('LH' if hemifield == 'left' else 'RH') + '_'
    while (filename + str(x) + '.csv') in os.listdir(data_path):
        x += 1

    # get everything shared from central:
    setup = localizeSetup(location=location, trackEyes=trackEyes, filefolder=eyetracking_path, filename=et_filename+str(x), task='distance', ID=ID) # data path is for the mapping data, not the eye-tracker data!

    # unpack all this
    win = setup['win']


    pyg_keyboard = key.KeyStateHandler()
    win.winHandle.push_handlers(pyg_keyboard)

    colors = setup['colors']
    col_both = colors['both']
    if hemifield == 'left':
        col_ipsi, col_contra = colors['left'], colors['right']
    if hemifield == 'right':
        col_contra, col_ipsi = colors['left'], colors['right']

    # if hemifield == 'left':
    #     col_ipsi, col_contra = colors['right'], colors['left']
    # if hemifield == 'right':
    #     col_contra, col_ipsi = colors['right'], colors['left']

    # print(colors)

    hiFusion = setup['fusion']['hi']
    loFusion = setup['fusion']['lo']

    blindspot = setup['blindspotmarkers'][hemifield]
    # print(blindspot.fillColor)
    
    fixation = setup['fixation']

    tracker = setup['tracker']

    # in order to set up the stimuli, we need the blind spot marker properties:


    left_prop  = setup['blindspotmarkers']['left_prop']
    right_prop = setup['blindspotmarkers']['right_prop']

    # spot_left    = left_prop['spot'] # polar coords?
    spot_left    = left_prop['cart']
    size_left    = left_prop['size']
    # ang_up_left  = left_prop['ang_up'] # angle for distance task away from BS locations
    # tar_left     = left_prop['tar']  # target distance for distance task

    # spot_right   = right_prop['spot']
    spot_right   = right_prop['cart']
    size_right   = right_prop['size']
    # ang_up_right = right_prop['ang_up'] # angle for distance task away from BS locations
    # tar_right    = right_prop['tar']  # target distance for distance task

    # longest axis of the blind spot marker:
    lax_left  = np.max(size_left)
    lax_right = np.max(size_right)

    # margin of 2 dva on either side
    dist_left  = 2 + lax_left  + 2
    dist_right = 2 + lax_right + 2