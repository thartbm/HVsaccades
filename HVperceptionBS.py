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
from psychopy.tools import monitorunittools
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
    # win.viewPos = [0,-5] # should also be applied to the blind spot mapping procedure!

    pyg_keyboard = key.KeyStateHandler()
    win.winHandle.push_handlers(pyg_keyboard)


    p2d = monitorunittools.pix2deg(1, win.monitor)
    winsize = win.monitor.getSizePix()
    vertical_range = winsize[1] * p2d # vertical range in DVA !!!!!!

    colors = setup['colors']
    print(colors)
    col_both = colors['both']
    if hemifield == 'left':
        # win.viewPos = [10,-3]
        col_ipsi, col_contra = colors['left'], colors['right']
    if hemifield == 'right':
        # win.viewPos = [-10,-3]
        col_contra, col_ipsi = colors['left'], colors['right']


    # stimuli
    point_1 = visual.ShapeStim( win=win,
                                units='deg',
                                colorSpace='rgb',
                                lineColor=None,
                                fillColor=col_both,
                                vertices=[[[.5,.1],[.5,-.1],[.1,-.1],[.1,-.5],[-.1,-.5],[-.1,-.1],[-.5,-.1],[-.5,.1],[-.1,.1],[-.1,.5],[.1,.5],[.1,.1]]],
                                pos = [0,0],
                                ori = 0,
                                size = 2,
                                )

    point_2 = visual.ShapeStim( win=win,
                                units='deg',
                                colorSpace='rgb',
                                lineColor=None,
                                fillColor=col_both,
                                vertices=[[[.5,.1],[.5,-.1],[.1,-.1],[.1,-.5],[-.1,-.5],[-.1,-.1],[-.5,-.1],[-.5,.1],[-.1,.1],[-.1,.5],[.1,.5],[.1,.1]]],
                                pos = [0,0],
                                ori = 45,
                                size = 2,
                                )

    point_3 = visual.Circle(win, radius = .5, pos = [0,0], units = 'deg', fillColor = col_both, lineColor = None)
    point_4 = visual.Circle(win, radius = .5, pos = [0,0], units = 'deg', fillColor = col_both, lineColor = None)

    # if hemifield == 'left':
    #     col_ipsi, col_contra = colors['right'], colors['left']
    # if hemifield == 'right':
    #     col_contra, col_ipsi = colors['right'], colors['left']

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
        win.viewPos = [10, -5]
        tracker.setCalibrationTargets( np.array([[0,0],  [5,0],[0,-5],[5,-5],  [0,5],[0,17],   [-10,5],[-10,17],[-10,-7],  [-15,11],[-15,-1],   [-20,5],[-20,17],[-20,-7],  [-25,11],[-25,-1] ]) ) #   [-3,0],[0,3],[3,0],[0,-3],     [6,6],[6,-6],[-6,6],[-6,-6]]) )
    if hemifield == 'right':
        prop = setup['blindspotmarkers']['right_prop']
        mult_fact = 1
        win.viewPos = [-10,-5]
        tracker.setCalibrationTargets( np.array([[0,0],  [-5,0],[0,-5],[-5,-5],  [0,5],[0,17],  [10,5],[10,17],[10,-7],  [15,11],[15,-1],   [20,5],[20,17],[20,-7],  [25,11],[25,-1]]) )


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

    angle_var = abs(np.arctan((bs_size[1]/4)/bs_pos_cart[0])/np.pi*180)
    
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

    # # conditions = pd.DataFrame({'bs_tilt': bs_tilt, 'ad_tilt': ad_tilt, 'eye': eye, 'dist_diff': dist_diff})

    # bs_tilt = [0, 90, 0] * 6
    # ad_tilt = [90, 0, 0] * 6
    # eye = ['both'] * 3 + ['ipsi'] * 3 + ['contra'] * 3 + ['both'] * 3 + ['ipsi'] * 3 + ['contra'] * 3
    # dist_diff = [-2] * 9 + [2] * 9

    # conditions = pd.DataFrame({'bs_tilt': bs_tilt, 'ad_tilt': ad_tilt, 'eye': eye, 'dist_diff': dist_diff})

    # cond_idx = list(range(len(conditions)))
    # blocks = []
    # n_blocks = 4
    # for block_no in range(n_blocks):
    #     block_def = {}
    #     block_def['block_no'] = block_no
    #     random.shuffle(cond_idx)
    #     block_def['trials'] = copy.deepcopy(cond_idx)
    #     block_def['instructions'] = 'press space to calibrate\n\nand start block ' + str(block_no+1) + ' / ' + str(n_blocks)
    #     blocks.append(block_def)

    # block_idx = 0
    trial_idx = 0

    # WE CAN ADD CONDITIIONS HERE...

    sc_bs_tilt = [      0,     90,      0,      0,     90,      0] # ,       90,       90]
    sc_ad_tilt = [     90,      0,      0,     90,      0,      0] # ,        0,        0]
    sc_eye =     [ 'ipsi', 'ipsi', 'ipsi', 'ipsi', 'ipsi', 'ipsi'] # , 'contra', 'contra']
    sc_start =   [  'min',  'min',  'min',  'max',  'max',  'max'] # ,    'min',    'max']

    sc_conditions = pd.DataFrame({'sc_bs_tilt': sc_bs_tilt, 'sc_ad_tilt': sc_ad_tilt, 'sc_eye': sc_eye, 'sc_start': sc_start})
    my_steps = list(np.arange(-3.5, 4.0, 0.5))
    sc_staircases = []
    for cond_idx in range(len(sc_conditions)):
        if sc_start[cond_idx] == 'min':
            idx = 0
        if sc_start[cond_idx] == 'max':
            idx = 14
        my_sc = SimpleStaircase( steps        = my_steps, 
                                 idx          = idx, 
                                 minTrials    = 30, 
                                 minReversals = 10, 
                                 info         = sc_conditions.iloc[cond_idx])
        sc_staircases.append(my_sc)


    # collect data in a dictionary:

    data =  {
            'participant':  [],
            'hemifield':    [],
            # 'blockno':      [],    # no block structure?
            'trialno':      [],
            'jitter':       [],    # ????
            'staircase':    [],    # which staircase was used for this trial (0-5 or maybe 0-7)
            'bs_tilt':      [],
            'aw_tilt':      [],
            'eye'    :      [],
            'bs_dist':      [],    # should be fixed
            'ad_dist':      [],    # variable by staircases
            'shown_first':  [],    # which pair was shown first? (1: bs or 2: ad)
            'response':     [],    # which pair was judged as larger? (1/left: first shown or 2/right: second shown)
            'rt':           []     # not strictly necessary?
            }


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

    # mouse_factor = 3.5     # this is no longer needed!

    not_done = True

    running = [sc.running for sc in sc_staircases]

    do_staircases = [idx for idx in range(len(running)) if running[idx]]

    trial_no = 0

    while not_done:

        # this should be done at the end of the trial
        # before inserting a break for people

        trial_no = trial_no + 1

        if len(do_staircases) == 0:
            # shuffle running staircases
            # do those one-by-one
            running = [sc.running for sc in sc_staircases]
            do_staircases = [idx for idx in range(len(running)) if running[idx]]
            random.shuffle(do_staircases)

        # pop one at random:
        this_sc = do_staircases.pop()
        staircase = sc_staircases[this_sc]
        
        bs_tilt = staircase.info['sc_bs_tilt']
        ad_tilt = staircase.info['sc_ad_tilt']
        eye     = staircase.info['sc_eye']

        # relatively unimportant, just randomize every trial:
        tpair = random.choice(['BS', 'AW'])

        jitter = 0 # distance jitter or angle jitter?

        print('block: %d/%d, trial %d/%d, BS: %d, AW: %d, %s, target: %s'%(block_idx+1, len(blocks), trial_idx+1, len(blocks[block_idx]['trials']), bs_tilt, aw_tilt, eye, tpair))

        bs_pos = pol2cart(bs_pos_pol[0] + jitter, bs_pos_pol[1], units='deg')
        aw_pos = pol2cart(aw_pos_pol[0] + jitter, aw_pos_pol[1], units='deg')

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
        # mult_fact depends on hemifield (left: -1, right: 1)
        # temp_pos = pol2cart(mult_fact * bs_tilt, test_dist/2, units='deg')
        temp_pos = pol2cart(        1 * bs_tilt, test_dist/2, units='deg')
        point_1.pos = [bs_pos[0] + temp_pos[0], bs_pos[1] + temp_pos[1]]
        point_2.pos = [bs_pos[0] - temp_pos[0], bs_pos[1] - temp_pos[1]]

        # temp_pos = pol2cart(mult_fact * ad_tilt, test_dist/2, units='deg')
        temp_pos = pol2cart(        1 * aw_tilt, test_dist/2, units='deg')
        point_3.pos = [aw_pos[0] + temp_pos[0], aw_pos[1] + temp_pos[1]]
        point_4.pos = [aw_pos[0] - temp_pos[0], aw_pos[1] - temp_pos[1]]

        if tpair == 'AW':
            point_1.pos, point_2.pos, point_3.pos, point_4.pos = point_3.pos, point_4.pos, point_1.pos, point_2.pos

        if abs(point_1.pos[0]) > abs(point_2.pos[0]):
            point_1.pos, point_2.pos = point_2.pos, point_1.pos


        # distance = (test_dist+dist_diff)/2 - (vertical_range/2)
        # mouse.setPos([0, distance*mouse_factor]) # set the mouse to the starting position for the adjustable pair
        
        # if trial_idx == 0:
        #     # show instruction to start with eye-tracker calibration
        #     visual.TextStim(win,
        #         blocks[block_idx]['instructions'], 
        #         height = 1, 
        #         wrapWidth=15,
        #         color = 'black').draw()
        #     win.flip()
        #     k = ['wait']
        #     while k[0] not in ['space']:
        #         k = event.waitKeys()

        #     event.clearEvents(eventType='keyboard') # just to be sure?

        #     # calibration
        #     # tracker.openfile()
        #     # tracker.startcollecting()
        #     tracker.calibrate()


        # add some info about trial to the eye-tracker data file:
        tracker.comment('next trial')
        time.sleep(2/500)


        start_time = time.time()

        # adds a little time in between trials:
        # probably looking somewhere else as well
        fixation.pos = random.sample([4,6,8,10],1) + random.sample([4,6,8,10],1)
        fixation.pos[0] = fixation.pos[0] * mult_fact
        waiting_for_fixation = True
        while waiting_for_fixation:
            fixation.draw()
            win.flip()
            if tracker.gazeInFixationWindow(fixloc=fixation.pos):
                waiting_for_fixation = False
        
        fixation.pos = [0,0]

        tracker.waitForFixation()

        # STIMULUS PRESENTATION:
        abort = False

        hiFusion.resetProperties()
        loFusion.resetProperties()
        
        stimulus_start = time.time()

        tracker.comment('stimulus on')

        while (time.time() - stimulus_start) < .50 and not abort:

            if tracker.gazeInFixationWindow():
                pass
            else:
                tracker.comment('fixation broken')
                abort = True
            
            fixation.draw()
            blindspot.draw()
            loFusion.draw()
            hiFusion.draw()

            opacity = 0

            # if (time.time() - stimulus_start) > .15:
            #     opacity = min(1, ((time.time() - stimulus_start) - .15) / .15)

            if (time.time() - stimulus_start) > .15:
                opacity = 1

            if (time.time() - stimulus_start) > .30:
                point_1.draw()
            if (time.time() - stimulus_start) > .40:
                point_2.draw()
            # other pair is always there:

            point_3.opacity = opacity
            point_4.opacity = opacity
            point_3.draw()
            point_4.draw()


            win.flip()

        # stimulus presented, now collect response
        waiting_for_response = True

        while waiting_for_response and not abort:
            
            # NO STIMULI ANYMORE?
            # show fixation
            # show fusion stimuli
            hiFusion.draw()
            loFusion.draw()
            blindspot.draw()
            fixation.draw()     # only one we need?


            win.flip()

            # either way, check keyboard for recalibration key (or quitting key)
            k = event.getKeys(['r', 'space']) # shouldn't this be space? like after the stimulus? this is confusing...
            if k and 'r' in k:
                # recalibrate
                # tracker.stopcollecting()
                print('recalibrating...')
                tracker.calibrate()
                # tracker.startcollecting()
            if k and 'space' in k:
                # response given, move on to next trial
                rt = time.time() - start_time
                waiting_for_response = False


        # if abort:

            # handle aborts?

        # store the collected data in the data frame
        # 
        # store the data frame as a csv:
        # data.to_csv()
        

        data['participant'].append(ID)
        data['hemifield'].append(hemifield)
        # data['blockno'.append(0)    # no block structure?
        data['trialno'].append(trial_no)
        data['jitter'].append(jitter)    # ????
        data['staircase'].append()    # which staircase was used for this trial (0-5 or maybe 0-7)
        data['bs_tilt'].append(bs_tilt)
        data['aw_tilt'].append(aw_tilt)
        data['eye'    ].append(eye)
        data['bs_dist'].append()    # should be fixed
        data['ad_dist'].append()    # variable by staircases
        data['shown_first'].append()    # which pair was shown first? (1: bs or 2: ad)
        data['response'].append()    # which pair was judged as larger? (1/left: first shown or 2/right: second shown)
        data['rt'].append()     # not strictly necessary?
        

        pd.DataFrame(data).to_csv(csv_filename, index=False)

        # print('recorded final distance: %0.3f dva'%(distance*2))


        if block_idx >= len(blocks):
            # done all the blocks... end task:
            not_done = False

    # end of task: stop eye-tracker recording, show end screen
    tracker.stopcollecting()
    tracker.closefile()
    tracker.shutdown()

    visual.TextStim(win,
        'THE END\n\nThanks!', 
        height = 1, 
        wrapWidth=15,
        color = 'black').draw()
    win.flip()
    k = ['wait']
    while k[0] not in ['space']:
        k = event.waitKeys()
    
    win.close()





class SimpleStaircase:
    def __init__(self,steps,idx,minTrials,minReversals,info):
        self.steps = steps
        self.idx = idx
        self.minTrials = minTrials
        self.minReversals = minReversals
        self.info = info # arbitrary properties: put a dictionary or list for multiple bits of info

        self.running = True
        self.responses = []

    def getValue(self):
        return(self.steps[self.idx])

    def update(self, response):
        self.responses.append(response)
        self.idx += response
        if self.idx < 0:
            self.idx = 0
        if self.idx >= len(self.steps):
            self.idx = len(self.steps) - 1
        if len(self.responses) > 1:
            status = False
            if sum(np.diff(self.responses) != 0) < self.minReversals:
                status = True
            if len(self.responses) < self.minTrials:
                status = True
            self.running = status

class UDStaircase:
    def __init__(self,steps,idx,minTrials,minReversals,up,down,info):
        self.steps = steps
        self.idx = idx
        self.minTrials = minTrials
        self.minReversals = minReversals
        self.up = up
        self.down = down
        self.info = info # arbitrary properties: put a dictionary or list for multiple bits of info

        self.running = True
        self.responses = []

    def getValue(self):
        return(self.steps[self.idx])

    def update(self, response):
        self.responses.append(response)
        if response == 1:
            self.idx += self.up
        if response == -1:
            self.idx -= self.down
        
        if self.idx < 0:
            self.idx = 0
        if self.idx >= len(self.steps):
            self.idx = len(self.steps) - 1
        
        if len(self.responses) > 1:
            status = False
            if sum(np.diff(self.responses) != 0) < self.minReversals:
                status = True
            if len(self.responses) < self.minTrials:
                status = True
            self.running = status

class DescreasingStepStaircase:
    def __init__(self,steps,idx,minTrials,minReversals,step,decrease,info):
        self.steps = steps
        self.idx = idx
        self.minTrials = minTrials
        self.minReversals = minReversals
        self.step = step
        self.decrease = decrease
        self.info = info # arbitrary properties: put a dictionary or list for multiple bits of info

        self.running = True
        self.responses = []
        self.reversals = 0

    def getValue(self):
        return(self.steps[self.idx])

    def update(self, response):
        self.responses.append(response)
        if response == 1:
            self.idx += self.step
        if response == -1:
            self.idx -= self.step
        
        if self.idx < 0:
            self.idx = 0
        if self.idx >= len(self.steps):
            self.idx = len(self.steps) - 1
        
        if len(self.responses) > 1:
            status = False
            if sum(np.diff(self.responses) != 0) > self.reversals:
                self.reversals += 1
                self.step = max(1,self.step-self.decrease)
            if self.reversals < self.minReversals:
                status = True
            if len(self.responses) < self.minTrials:
                status = True
            self.running = status