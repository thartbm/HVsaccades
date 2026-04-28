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



# import psychopy
from psychopy import visual, gui, event
# from psychopy import core, data
from psychopy.tools.coordinatetools import pol2cart
# from psychopy.tools.coordinatetools import cart2pol
import numpy as np
import random, os, time, copy
# import datetime
from glob import glob
# from itertools import compress

from psychopy.hardware import keyboard
from pyglet.window import key

import pandas as pd


import sys
sys.path.append(os.path.join('..', 'EyeTracking'))
from EyeTracking import localizeSetup

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

    main_path = 'data/perception/'
    data_path = main_path
    eyetracking_path = main_path + 'eyetracking/' + ID + '/'

    # should already be there because of calibration tasks
    os.makedirs(data_path, exist_ok=True)
    os.makedirs(eyetracking_path, exist_ok=True)


    # create data output filename:
    x = 1
    # filename = '_dist_' + ('LH' if hemifield == 'left' else 'RH') + '_' + ID + '_'
    filename = ID + '_HVpercept_' + ('LH' if hemifield == 'left' else 'RH') + '_'
    while (filename + str(x) + '.csv') in os.listdir(data_path):
        x += 1

    csv_filename = data_path + filename + str(x) + '.csv'

    # create eye-tracking output filename:
    x = 1
    et_filename = 'HVpr' + ('LH' if hemifield == 'left' else 'RH')
    while len(glob(eyetracking_path + et_filename + str(x) + '.*')):
        x += 1

    # get everything shared from central:
    setup = localizeSetup(location=location, trackEyes=trackEyes, filefolder=eyetracking_path, filename=et_filename+str(x), task='perception', ID=ID) # data path is for the mapping data, not the eye-tracker data!

    # unpack all this
    win = setup['win']
    win.viewPos = [0,-5] # should also be applied to the blind spot mapping procedure!

    pyg_keyboard = key.KeyStateHandler()
    win.winHandle.push_handlers(pyg_keyboard)

    colors = setup['colors']
    print(colors)
    col_both = colors['both']
    if hemifield == 'left':
        col_ipsi, col_contra = colors['left'], colors['right']
    if hemifield == 'right':
        col_contra, col_ipsi = colors['left'], colors['right']

    # stimuli
    point_1 = visual.Circle(win, radius = .5, pos = [0,0], units = 'deg', fillColor = col_both, lineColor = None)
    point_2 = visual.Circle(win, radius = .5, pos = [0,0], units = 'deg', fillColor = col_both, lineColor = None)
    point_3 = visual.Circle(win, radius = .5, pos = [0,0], units = 'deg', fillColor = col_both, lineColor = None)
    point_4 = visual.Circle(win, radius = .5, pos = [0,0], units = 'deg', fillColor = col_both, lineColor = None)

    # if hemifield == 'left':
    #     col_ipsi, col_contra = colors['right'], colors['left']
    # if hemifield == 'right':
    #     col_contra, col_ipsi = colors['right'], colors['left']

    # print(colors)

    hiFusion = setup['fusion']['hi']
    loFusion = setup['fusion']['lo']

    loFusion.pos = [0, -10]
    if hemifield == 'left':
        hiFusion.pos = [10, 0]
    if hemifield == 'right':
        hiFusion.pos = [-10, 0]

    blindspot = setup['blindspotmarkers'][hemifield]
    # print(blindspot.fillColor)
    
    fixation   = setup['fixation']
    fixation_x = setup['fixation_x']

    tracker = setup['tracker']

    # additional hardware is a mouse object:

    mouse = event.Mouse(visible=False, win=win) #invisible

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

    bs_pos_pol = prop['spot']
    bs_pos_cart = prop['cart']
    bs_size = prop['size']

    # # longest axis of the blind spot marker:
    # lax_left  = np.max(size_left)
    # lax_right = np.max(size_right)

    lax = np.max(bs_size)

    # # margin of 2 dva on either side
    # dist_left  = 2 + lax_left  + 2
    # dist_right = 2 + lax_right + 2

    test_dist = 3 + lax + 3

    bs_dist = sum(np.array(bs_pos_cart)**2)**0.5

    angle_var = abs(np.arctan((bs_size[1]/3)/bs_pos_cart[0])/np.pi*180)
    
    margin = 2

    # now we want an isosecles triangle with the two legs equal to test_dist, and the base equal to lax
    # an isosecles triangle can be split into two congruent right triangles, where the hypotenuse is test_dist, and one leg is lax/2
    # we want the angle between the hypothenuse and the side of unknown length
    # print(test_dist)
    # print(margin)
    # print(bs_dist)
    alpha = np.arcsin(((test_dist+margin)/2)/bs_dist) * 2 * 180/np.pi
    
    # in the right hemifield, we add the alpha, on the left, we subtract it
    # print(pos_polar[0])
    # print(alpha)
    # print(mult_fact)
    # print(alpha * mult_fact)
    # print(bs_dist)

    ad_pos_pol = [bs_pos_pol[0] + (alpha * mult_fact), bs_dist]
    ad_pos_cart = pol2cart(bs_pos_pol[0] + (alpha * mult_fact), bs_dist, units='deg')

    # print(ad_pos)

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

    # bs_tilt = [0, 0, 0, -45, 45] * 6
    # ad_tilt = [0, -45, 45, 0, 0] * 6
    # eye = ['both'] * 5 + ['ipsi'] * 5 + ['contra'] * 5 + ['both'] * 5 + ['ipsi'] * 5 + ['contra'] * 5
    # dist_diff = [-2] * 15 + [2] * 15

    # conditions = pd.DataFrame({'bs_tilt': bs_tilt, 'ad_tilt': ad_tilt, 'eye': eye, 'dist_diff': dist_diff})

    bs_tilt = [0, 90, 0] * 6
    ad_tilt = [90, 0, 0] * 6
    eye = ['both'] * 3 + ['ipsi'] * 3 + ['contra'] * 3 + ['both'] * 3 + ['ipsi'] * 3 + ['contra'] * 3
    dist_diff = [-2] * 9 + [2] * 9

    conditions = pd.DataFrame({'bs_tilt': bs_tilt, 'ad_tilt': ad_tilt, 'eye': eye, 'dist_diff': dist_diff})

    cond_idx = list(range(len(conditions)))
    blocks = []
    n_blocks = 3
    for block_no in range(n_blocks):
        block_def = {}
        block_def['block_no'] = block_no
        random.shuffle(cond_idx)
        block_def['trials'] = copy.deepcopy(cond_idx)
        block_def['instructions'] = 'press space to calibrate\n\nand start block ' + str(block_no+1) + ' / ' + str(n_blocks)
        blocks.append(block_def)    

    block_idx = 0
    trial_idx = 0


    # collect data in a dictionary:

    data = { 'participant':  [],
             'hemifield':    [],
             'blockno':      [],
             'trialno':      [],
             'jitter':       [],
             'bs_tilt':      [],
             'aw_tilt':      [],
             'eye'    :      [],
             'bs_dist':      [],
             'start_diff':   [],
             'rt':           [],
             'final_dist':   []}


    # show first instructions
    visual.TextStim(win,
        'Throughout the task, use the mouse adjust the upper dot pair so that the distance between the dots matches the distance of the lower pair.\n\nPress space to continue.', 
        height = 1, 
        wrapWidth=15,
        color = 'black').draw()
    win.flip()
    k = ['wait']
    while k[0] not in ['space']:
        k = event.waitKeys()
    
    event.clearEvents(eventType='keyboard') # just to be sure?

    tracker.openfile()
    tracker.startcollecting()
    
    # fixation.draw()
    # win.flip()

    mouse_factor = 2

    not_done = True

    while not_done:

        # print(block_idx)
        # print(trial_idx)
        # print(blocks)
        # print(blocks[block_idx])

        # properties of the current trial:
        cond_idx = blocks[block_idx]['trials'][trial_idx]

        bs_tilt = conditions['bs_tilt'][cond_idx]
        ad_tilt = conditions['ad_tilt'][cond_idx]
        eye = conditions['eye'][cond_idx]
        dist_diff = conditions['dist_diff'][cond_idx]

        jitter = random.sample([-1,-0.5,0,0.5,1], 1)[0] * angle_var

        bs_pos = pol2cart(bs_pos_pol[0] + jitter, bs_pos_pol[1], units='deg')
        ad_pos = pol2cart(ad_pos_pol[0] + jitter, ad_pos_pol[1], units='deg')

        if eye == 'both':
            point_color = col_both
        elif eye == 'ipsi':
            point_color = col_ipsi
        elif eye == 'contra':
            point_color = col_contra
        point_1.fillColor = point_color
        point_2.fillColor = point_color
        point_3.fillColor = point_color
        point_4.fillColor = point_color

        # bs points are non-adjustable and points 1 & 2:
        temp_pos = pol2cart(bs_tilt, test_dist/2, units='deg')
        point_1.pos = [bs_pos[0] + temp_pos[0], bs_pos[1] + temp_pos[1]]
        point_2.pos = [bs_pos[0] - temp_pos[0], bs_pos[1] - temp_pos[1]]

        distance = (test_dist+dist_diff)/2
        mouse.setPos([0, distance*mouse_factor]) # set the mouse to the starting position for the adjustable pair
        



        if trial_idx == 0:
            # show instruction to start with eye-tracker calibration
            visual.TextStim(win,
                blocks[block_idx]['instructions'], 
                height = 1, 
                wrapWidth=15,
                color = 'black').draw()
            win.flip()
            k = ['wait']
            while k[0] not in ['space']:
                k = event.waitKeys()

            event.clearEvents(eventType='keyboard') # just to be sure?

            # calibration
            # tracker.openfile()
            # tracker.startcollecting()
            tracker.calibrate()

        waiting_for_response = True

        hiFusion.resetProperties()
        loFusion.resetProperties()



        start_time = time.time()

        # adds a little time in between trials:
        # probably looking somewhere else as well
        fixation.pos = random.sample([-8,-6,-4,4,6,8],1) + random.sample([-8,-6,-4,4,6,8],1)
        waiting_for_fixation = True
        while waiting_for_fixation:
            fixation.draw()
            win.flip()
            if tracker.gazeInFixationWindow(fixloc=fixation.pos):
                waiting_for_fixation = False
        
        fixation.pos = [0,0]

        tracker.waitForFixation()


        while waiting_for_response:
            
            # show fixation
            # show fusion stimuli
            hiFusion.draw()
            loFusion.draw()
            blindspot.draw()

            t = time.time() % 1
            draw_pair_1 = True
            draw_pair_2 = True
            if 0 < t < 0.2:
                draw_pair_1 = False
            if 0.5 < t < 0.7:
                draw_pair_2 = False

            # check fixation
            # if fixating:
            # - show stimuli
            # - use mouse to adjust the distance of the adjustable pair
            # - check for response (e.g. spacebar press)
            
            if tracker.gazeInFixationWindow(fixloc=fixation.pos):
                fixation.draw()    
                if draw_pair_1:
                    point_1.draw()
                    point_2.draw()

                # adjustable points are points 3 & 4:
                distance = mouse.getPos()[1]/mouse_factor
                # print(distance) # one number
                temp_pos = pol2cart(ad_tilt+jitter, distance, units='deg')
                # print(ad_pos) # tuple of arrays?
                # print(temp_pos) # tuple of numbers
                p3p = [ad_pos[0] + temp_pos[0], ad_pos[1] + temp_pos[1]]
                p4p = [ad_pos[0] - temp_pos[0], ad_pos[1] - temp_pos[1]]
                # print(p3p, p4p)
                point_3.pos = p3p
                point_4.pos = p4p

                if draw_pair_2:
                    point_3.draw()
                    point_4.draw()
            else:
                mouse.setPos([0, distance*mouse_factor]) # keep mouse at a reasonable position if not fixating
                fixation_x.draw()
            
            win.flip()

            # either way, check keyboard for recalibration key (or quitting key)
            k = event.getKeys(['r', 'space']) # shouldn't this be space? like after the stimulus? this is confusing...
            if k and 'r' in k:
                # recalibrate
                # tracker.stopcollecting()
                tracker.calibrate()
                # tracker.startcollecting()
            if k and 'space' in k:
                # response given, move on to next trial
                rt = time.time() - start_time
                waiting_for_response = False


        # store the collected data in the data frame
        # 
        # store the data frame as a csv:
        # data.to_csv()
        data['participant'].append(ID)
        data['hemifield'].append(hemifield)
        data['blockno'].append(block_idx+1)
        data['trialno'].append(trial_idx+1)
        data['jitter'].append(jitter)
        data['bs_tilt'].append(bs_tilt)
        data['aw_tilt'].append(ad_tilt)
        data['eye'].append(eye)
        data['bs_dist'].append(test_dist)
        data['start_diff'].append(dist_diff)
        data['rt'].append(rt)
        data['final_dist'].append(distance*2) 

        pd.DataFrame(data).to_csv(csv_filename, index=False)

        # end of trial: increase trial & block indices
        trial_idx = trial_idx + 1

        if trial_idx >= len(blocks[block_idx]['trials']):
            # done all trials in the block... next block:
            block_idx = block_idx + 1
            trial_idx = 0

        if block_idx >= len(blocks):
            # done all the blocks... end task:
            not_done = False

    # end of task: stop eye-tracker recording, show end screen
    tracker.stopcollecting()
    tracker.closefile()
    tracker.shutdown()

    visual.TextStim(win,
        'THE END\n\nThank you for participating!', 
        height = 1, 
        wrapWidth=15,
        color = 'black').draw()
    win.flip()
    k = ['wait']
    while k[0] not in ['space']:
        k = event.waitKeys()
    
    win.close()



