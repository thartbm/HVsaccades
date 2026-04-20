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

import pandas as pd


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

    if hemifield == 'left':
        prop  = setup['blindspotmarkers']['left_prop']
        mult_fact = -1
    if hemifield == 'right':
        prop = setup['blindspotmarkers']['right_prop']
        mult_fact = 1

    # # spot_left    = left_prop['spot'] # polar coords?
    # spot_left    = left_prop['cart']
    # size_left    = left_prop['size']
    # # ang_up_left  = left_prop['ang_up'] # angle for distance task away from BS locations
    # # tar_left     = left_prop['tar']  # target distance for distance task

    # # spot_right   = right_prop['spot']
    # spot_right   = right_prop['cart']
    # size_right   = right_prop['size']
    # # ang_up_right = right_prop['ang_up'] # angle for distance task away from BS locations
    # # tar_right    = right_prop['tar']  # target distance for distance task

    pos_polar = prop['spot']
    test_pos = prop['cart']
    size = prop['size']

    # # longest axis of the blind spot marker:
    # lax_left  = np.max(size_left)
    # lax_right = np.max(size_right)

    lax = np.max(size)

    # # margin of 2 dva on either side
    # dist_left  = 2 + lax_left  + 2
    # dist_right = 2 + lax_right + 2

    test_dist = 2 + lax + 2

    bs_dist = (np.array(test_pos)**2)**0.5
    
    margin = 2

    # now we want an isosecles triangle with the two legs equal to test_dist, and the base equal to lax
    # an isosecles triangle can be split into two congruent right triangles, where the hypotenuse is test_dist, and one leg is lax/2
    # we want the angle between the hypothenuse and the side of unknown length
    alpha = np.arcsin(((test_dist+margin)/2)/bs_dist) * 2
    
    # in the right hemifield, we add the alpha, on the left, we subtract it
    foil_pos = pol2cart(pos_polar[0] + (alpha * mult_fact), bs_dist)

    # conditions we want to test:

    # TILTS:
    # - both horizontal
    # - blind spot tilted 45 degrees, one way
    # - other way
    # - comparison tilted 45 degrees, one way
    # - other way

    # EYE:
    # - blind spot eye only
    # - both eyes
    # - other eye?

    # this would make 5 * 3 = 15 conditions

    # we want to repeat each condition some numner of times
    # we can adjust the starting size of the adjustable pair

    # if we use 2 starting distances (+2 dva and -2 dva?)
    # we could have 30 trials per block, and do 150 trials total
    # that would be 10 repetitions per condition
    # and we repeat this for both hemifields
    # (any cancelled trials will be repeated at the end of the block, so it's always 10)

    # 10 repetitions means a good distributions within each condition separately
    # but we could also do 8 or 6... that would make for a shorter task
    # and more of a stochastic approach: we need statistics and large N

    bs_tilt = [0, 0, 0, -45, 45] * 6
    aw_tilt = [0, -45, 45, 0, 0] * 6
    eye = ['both'] * 5 + ['ipsi'] * 5 + ['contra'] * 5 + ['both'] * 5 + ['ipsi'] * 5 + ['contra'] * 5
    dist_diff = [-2] * 15 + [2] * 15

    conditions = pd.DataFrame({'bs_tilt': bs_tilt, 'aw_tilt': aw_tilt, 'eye': eye, 'dist_diff': dist_diff})

    cond_idx = list(range(len(conditions)))
    blocks = []
    for block_no in range(5):
        block_def = {}
        block_def['block_no'] = block_no
        block_def['trials'] = random.shuffle(cond_idx.copy())
        block_def['instructions'] = 'press space to start block ' + str(block_no+1) + ' out of 5'
        blocks.append(block_def)    

    block_idx = 0
    trial_idx = 0


    # collect data in a dictionary:

    data = { 'blockno':    [],
             'trialno':    [],
             'bs_tilt':    [],
             'aw_tilt':    [],
             'eye'    :    [],
             'start_diff': [],
             'rt':         [],
             'final_dist': []}


    not_done = True

    while not_done:

        # properties of the current trial:
        cond_idx = blocks[block_idx][trial_idx]

        bs_tilt = conditions['bs_tilt'][cond_idx]
        aw_tilt = conditions['aw_tilt'][cond_idx]
        eye = conditions['eye'][cond_idx]
        dist_diff = conditions['dist_diff'][cond_idx]


        # if trial_idx = 0:
        # - show instructions
        # - do calibration




        # store the collected data as a csv:
        # data.to_csv()

        # end of trial: increase trial & block indices
        trial_idx = trial_idx + 1

        if trial_idx >= len(block_def[block_idx]):
            # done all trials in the block... next block:
            block_idx = block_idx + 1
            trial_idx = 0

        if block_idx >= len(block_def):
            # done all the blocks... end task:
            not_done = False






