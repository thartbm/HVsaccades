import time, os, random, sys, json, copy
import numpy as np
import pandas as pd
from psychopy import visual, core, event, monitors, tools
from psychopy.hardware import keyboard

# altenative keyboard read-out?
from pyglet.window import key

# for tactile stimulation:
# import time # already imported elseweher
# from serial import Serial


# calibration / eyetracking imports ----
sys.path.append(os.path.join('..', 'EyeTracking'))
from EyeTracking import EyeTracker

# import math
# import time
# from glob import glob

from psychopy import gui, data
from psychopy.tools.coordinatetools import pol2cart, cart2pol



def runExperiment(ID          = None, 
                  expno       = 1,
                  eyetracking = False):


    cfg = {}
    cfg['expno'] = expno
    cfg['eyetracking'] = eyetracking

    # embed in try-catch-else-finally block?

    cfg = setParticipant(cfg, ID)

    cfg = setWindow(cfg, setup='livetrack')

    if cfg['eyetracking']:
        cfg = setEyetracker(cfg)
    else:
        print('what are you even doing?')

    cfg = getTasks(cfg)

    cfg = runTasks(cfg)





def setParticipant(cfg, ID):

    if ID == None:
        raise('participant ID can not be None')
    elif isinstance(ID, str):
        cfg['ID'] = ID
    else:
        raise('participant ID should be a string')


    # set up folder's for groups and participants to store the data
    # if check_path: # always check paths!
        # print('checking paths:')
    for thisPath in ['../data', '../data/%s'%(cfg['ID'])]:
        # print(' - %s'%(thisPath))
        if os.path.exists(thisPath):
            if not(os.path.isdir(thisPath)):
                # os.makedirs
                raise('"%s" is not a folder'%(thisPath))
            else:
                if (thisPath == '../data/%s'%(cfg['ID'])):
                    raise('participant already exists')

        else:
            # print('making folder: "%s"', thisPath)
            os.mkdir(thisPath)

    
    # store data in folder for task / exp no / participant:
    cfg['datadir'] = '../data/%s/'%(cfg['ID'])

    # we need to seed the random number generator:
    random.seed('HVsaccades' + ID)

    return cfg



def setWindow(cfg, setup='livetrack'):

    gammaGrid = np.array([[0., 1., 1., np.nan, np.nan, np.nan],
                          [0., 1., 1., np.nan, np.nan, np.nan],
                          [0., 1., 1., np.nan, np.nan, np.nan],
                          [0., 1., 1., np.nan, np.nan, np.nan]], dtype=float)

    # # # # # # # # # # #
    # LIVETRACK specs

    # gammaGrid = np.array([ [  0., 135.44739,  2.4203537, np.nan, np.nan, np.nan  ],
    #                        [  0.,  27.722954, 2.4203537, np.nan, np.nan, np.nan  ],
    #                        [  0.,  97.999275, 2.4203537, np.nan, np.nan, np.nan  ],
    #                        [  0.,   9.235623, 2.4203537, np.nan, np.nan, np.nan  ]  ], dtype=np.float32)

    # resolution = [1920, 1080] # in pixels
    # size       = [59.8, 33.6] # in cm
    # distance   = 49.53 # in cm
    # screen     = 1  # index on the system: 0 = first monitor, 1 = second monitor, and so on

    # # # # # # # # # # #

    waitBlanking = False


    if setup == 'livetrack':
        gammaGrid = np.array([ [  0., 135.44739,  2.4203537, np.nan, np.nan, np.nan  ],
                               [  0.,  27.722954, 2.4203537, np.nan, np.nan, np.nan  ],
                               [  0.,  97.999275, 2.4203537, np.nan, np.nan, np.nan  ],
                               [  0.,   9.235623, 2.4203537, np.nan, np.nan, np.nan  ]  ], dtype=float)

        resolution = [1920, 1080] # in pixels
        size       = [59.8, 33.6] # in cm
        distance   = 49.53 # in cm
        screen     = 1  # index on the system: 0 = first monitor, 1 = second monitor, and so on


    # for vertical tablet setup:
    if setup == 'tablet':
        #gammaGrid = np.array([[0., 136.42685, 1.7472667, np.nan, np.nan, np.nan],
        #                      [0.,  26.57937, 1.7472667, np.nan, np.nan, np.nan],
        #                      [0., 100.41914, 1.7472667, np.nan, np.nan, np.nan],
        #                      [0.,  9.118731, 1.7472667, np.nan, np.nan, np.nan]], dtype=float)

        gammaGrid = np.array([[  0., 107.28029,  2.8466334, np.nan, np.nan, np.nan],
                              [  0.,  22.207165, 2.8466334, np.nan, np.nan, np.nan],
                              [  0.,  76.29962,  2.8466334, np.nan, np.nan, np.nan],
                              [  0.,   8.474467, 2.8466334, np.nan, np.nan, np.nan]], dtype=float)

        waitBlanking = True
        resolution = [1680, 1050]
        size = [47, 29.6]
        distance = 60
        screen = 1

        wacomOneCM = resolution[0] / 31.1

    if setup == 'laptop':
    # for my laptop:
        waitBlanking = True
        resolution   = [1920, 1080]
        size = [34.5, 19.5]
        distance = 40
        screen = 1

        wacomOneCM = resolution[0] / 29.5


    mymonitor = monitors.Monitor(name='temp',
                                 distance=distance,
                                 width=size[0])
    mymonitor.setGammaGrid(gammaGrid)
    mymonitor.setSizePix(resolution)

    cfg['gammaGrid']    = list(gammaGrid.reshape([np.size(gammaGrid)]))
    cfg['waitBlanking'] = waitBlanking
    #cfg['resolution']   = resolution

    cfg['hw'] = {}

    # to be able to convert degrees back into pixels/cm
    cfg['hw']['mon'] = mymonitor

    #cfg['hw']['groove'] = [ tools.monitorunittools.pix2deg( (resolution[0]/2) - (5*wacomOneCM), cfg['hw']['mon'], correctFlat=False),
    #                        tools.monitorunittools.pix2deg( (resolution[0]/2) + (5*wacomOneCM), cfg['hw']['mon'], correctFlat=False) ]

    # cfg['trackextent'] = tools.monitorunittools.pix2deg( (5*wacomOneCM), cfg['hw']['mon'], correctFlat=False)

    # first set up the window and monitor:
    cfg['hw']['win'] = visual.Window( fullscr      = True,
                                      size         = resolution,
                                      units        = 'deg',
                                      waitBlanking = waitBlanking,
                                      color        = [0,0,0],
                                      monitor      = mymonitor,
                                      screen       = screen)
                                      # for anaglyphs: blendmode='add' !!!

    # res = cfg['hw']['win'].size
    # cfg['resolution'] = [int(x) for x in list(res)]
    # cfg['relResolution'] = [x / res[1] for x in res]

    # print(cfg['resolution'])
    # print(cfg['relResolution'])

    return(cfg)


def getStimuli(cfg):


    cfg['hw']['fixation'] = visual.TargetStim(win = cfg['hw']['win'],
                                              radius = 0.25,
                                              fillColor = [-1,-1,-1],
                                              borderColor = None,
                                              lineWidth=0,
                                              innerRadius=0.01,
                                              innerFillColor=[1,1,1],
                                              innerBorderColor=None,
                                              innerLineWidth=None,
                                              pos=[0,0])

    cfg['hw']['first'] = visual.TargetStim(win = cfg['hw']['win'],
                                              radius = 0.25,
                                              fillColor = [-1,-1,1],
                                              borderColor = None,
                                              lineWidth=0,
                                              innerRadius=0.01,
                                              innerFillColor=[1,1,1],
                                              innerBorderColor=None,
                                              innerLineWidth=None,
                                              pos=[0,0])

    cfg['hw']['second'] = visual.TargetStim(win = cfg['hw']['win'],
                                              radius = 0.25,
                                              fillColor = [1,-1,-1],
                                              borderColor = None,
                                              lineWidth=0,
                                              innerRadius=0.01,
                                              innerFillColor=[1,1,1],
                                              innerBorderColor=None,
                                              innerLineWidth=None,
                                              pos=[0,0])

    cfg['hw']['text'] = visual.TextStim(win=cfg['hw']['win'],
                                        text='',
                                        pos=[0,0]
                                        )

    return(cfg)


def getTasks(cfg):

    if cfg['expno']==1:

        condictionary = [

                         # crossing a meridian:

                         {'test':'down-right', 'first':[  5,  5], 'second':[  5, -5]},
                         {'test':'down-left',  'first':[ -5,  5], 'second':[ -5, -5]},

                         {'test':'up-right',   'first':[  5, -5], 'second':[  5,  5]},
                         {'test':'up-left',    'first':[ -5, -5], 'second':[ -5,  5]},

                         {'test':'left-hi',    'first':[  5,  5], 'second':[ -5,  5]},
                         {'test':'left-lo',    'first':[  5, -5], 'second':[ -5, -5]},

                         {'test':'right-hi',   'first':[ -5,  5], 'second':[  5,  5]},
                         {'test':'right-lo',   'first':[ -5, -5], 'second':[  5, -5]},

                         # along a meridian:

                         {'test':'down-mid',   'first':[  0,  5], 'second':[  0, -5]},
                         {'test':'up-mid',     'first':[  0, -5], 'second':[  0,  5]},
                         {'test':'left-mid',   'first':[  5,  0], 'second':[ -5,  0]}, 
                         {'test':'right-mid',  'first':[ -5,  0], 'second':[  5,  0]},

                         # no meridians:

                         {'test':'right-q1',   'first':[  5,  5], 'second':[ 15,  5]},
                         {'test':'up-q1',      'first':[  5,  5], 'second':[  5, 15]},

                         {'test':'left-q2',    'first':[ -5,  5], 'second':[-15,  5]},
                         {'test':'up,q2',      'first':[ -5,  5], 'second':[ -5, 15]},
                         
                         {'test':'left-q3',    'first':[ -5, -5], 'second':[-15, -5]},
                         {'test':'down-q3',    'first':[ -5, -5], 'second':[ -5,-15]},

                         {'test':'right-q4',   'first':[  5, -5], 'second':[ 15, -5]},
                         {'test':'down-q4',    'first':[  5, -5], 'second':[  5,-15]},


                         ]

        return( dictToBlockTrials(cfg=cfg, condictionary=condictionary, nblocks=1, nrepetitions=5, shuffle=True) )


def dictToBlockTrials(cfg, condictionary, nblocks, nrepetitions, shuffle=True):

    cfg['conditions'] = condictionary

    blocks = []
    for block in range(nblocks):

        blockconditions = []

        for repeat in range(nrepetitions):
            trialtypes = list(range(len(condictionary)))
            if shuffle:
                random.shuffle(trialtypes)
            blockconditions += trialtypes

        blocks += [{'trialtypes':blockconditions,
                    'instruction':'get ready for block %d of %d\npress enter to start'%(block+1,nblocks)}]

    cfg['blocks'] = blocks

    return(cfg)


def runTasks(cfg):


    if not('currentblock' in cfg):
        cfg['currentblock'] = 0
    if not('currenttrial' in cfg):
        cfg['currenttrial'] = 0

    if cfg['eyetracking']:
        cfg['hw']['tracker'].startcollecting()

    while cfg['currentblock'] < len(cfg['blocks']):

        # do the trials:
        cfg['currenttrial'] = 0

        showInstruction(cfg)

        # after instructions, calibrate:
        if cfg['eyetracking']:
            cfg['hw']['tracker'].calibrate()

        while cfg['currenttrial'] < len(cfg['blocks'][cfg['currentblock']]['trialtypes']):

            print([cfg['currenttrial'], len(cfg['blocks'][cfg['currentblock']]['trialtypes'])])

            trialtype = cfg['blocks'][cfg['currentblock']]['trialtypes'][cfg['currenttrial']]
            trialdict = cfg['conditions'][trialtype]

            cfg = doTrial(cfg)
            saveCfg(cfg)

            cfg['currenttrial'] += 1

        cfg['currentblock'] += 1



    return(cfg)


def showInstruction(cfg):

    cfg['hw']['text'].text = cfg['blocks'][cfg['currentblock']]['instruction']

    waiting_for_response = True

    while waiting_for_response:

        cfg['hw']['text'].draw()
        cfg['hw']['win'].flip()

        keys = event.getKeys(keyList=['enter', 'return', 'escape'])
        if len(keys):
            if 'enter' in keys:
                waiting_for_response = False
            if 'return' in keys:
                waiting_for_response = False
            if 'escape' in keys:
                cleanExit(cfg)



def setEyetracker(cfg):

    # use LiveTrack to check fixation on both eyes:
    # tracker = 'livetrack'
    trackEyes = [True,True]

    # do not store any files anywhere:
    filefolder = cfg['datadir']
    filename = '%s_exp%d.csv'%(cfg['ID'],cfg['expno'])

    colors = {'back' : [ 0, 0, 0],
              'both' : [-1,-1,-1]} # only for EyeLink
    
    ET = EyeTracker( tracker           = 'livetrack',
                     trackEyes         = trackEyes,
                     fixationWindow    = 2.0,
                     minFixDur         = 0.2,
                     fixTimeout        = 3.0,
                     psychopyWindow    = cfg['hw']['win'],
                     filefolder        = filefolder,
                     filename          = filename,
                     samplemode        = 'average',
                     calibrationpoints = 9,
                     colors            = colors ) # only for EyeLink

    ET.initialize(calibrationPoints = np.array([[0,0],   [10,0],[0,10],[-10,0],[0,-10],  [15,15],[-15,15],[-15,-15],[15,-15]  ]) )

    cfg['hw']['tracker'] = ET

    return(cfg)



def doTrial(cfg):

    trialtype = cfg['blocks'][cfg['currentblock']]['trialtypes'][cfg['currenttrial']]
    # trialdict = cfg['conditions'][trialtype]
    trialdict = copy.deepcopy(cfg['conditions'][trialtype])

    if 'test' in trialdict.keys():
        test = trialdict['test']
    else:
        test = 'untrial'
        trialdict['test'] = test
    
    if 'first' in trialdict.keys():
        first = trialdict['first']
    else:
        raise('first fixation not set for trial type %d')%(trialtype)

    if 'second' in trialdict.keys():
        second = trialdict['second']
    else:
        raise('second fixation not set for trial type %d')%(trialtype)



    cfg['hw']['first'].pos  = first
    cfg['hw']['second'].pos = second

    # put 'test' label into eyetracker data as comment
    # put first and second fixation positions in eyetracker data as well

    # wait for fixation
    #     if this fails:
    #     - recalibrate
    #     - keep doing this

    # show both locations for X ms
    # check fixation again... if it fails durding a... (200 ms?) interval:
    #     - restart trial?

    # detect saccades / fixations? or wait 1.5 seconds?

    # comment that recording is over

    # space bar to end trial and start next



    return(cfg)



def cleanExit(cfg):

    cfg['expfinish'] = time.time()

    saveCfg(cfg)

    print('cfg stored as json')

    cfg['hw']['win'].close()

    return(cfg)

def saveCfg(cfg):

    scfg = copy.copy(cfg)
    del scfg['hw']

    with open('%scfg.json'%(cfg['datadir']), 'w') as fp:
        json.dump(scfg, fp,  indent=4)

