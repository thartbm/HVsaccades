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

    cfg = getStimuli(cfg)

    if cfg['eyetracking']:
        cfg = setEyetracker(cfg)
    else:
        print('what are you even doing?')

    cfg = getTasks(cfg)

    cfg = runTasks(cfg)

    cfg = exportData(cfg)

    cleanExit(cfg)





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
    for thisPath in ['data', 'data/perception/', 'data/perception/%s'%(cfg['ID'])]:
        print(' - %s'%(thisPath))
        if os.path.exists(thisPath):
            if not(os.path.isdir(thisPath)):
                # os.makedirs
                raise('"%s" is not a folder'%(thisPath))
            else:
                if (thisPath == 'data/perception/%s'%(cfg['ID'])):
                    raise('participant already exists')

        else:
            print('making folder: "%s"', thisPath)
            os.mkdir(thisPath)

    
    # store data in folder for task / exp no / participant:
    cfg['datadir'] = 'data/perception/%s/'%(cfg['ID'])

    # we need to seed the random number generator:
    random.seed('HVperception' + ID)

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

    cfg['hw'] = {}

    cfg['hw']['gammaGrid']    = list(gammaGrid.reshape([np.size(gammaGrid)]))
    cfg['waitBlanking']       = waitBlanking
    #cfg['resolution']         = resolution


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



    cfg['hw']['fixation'] = visual.ShapeStim(cfg['hw']['win'], 
                                pos = [0,0],
                                vertices = ((.1,.1),(.5,.1),(.5,-.1), (.1,-.1), (.1,-.5),(-.1,-.5),(-.1,-.1),(-.5,-.1),(-.5,.1),(-.1,.1),(-.1,.5),(.1,.5),(.1,.1)), 
                                lineWidth = 0, 
                                units = 'deg', 
                                size = (1, 1), # might be too small?
                                closeShape = True, 
                                lineColor = None,
                                fillColor=[-1,-1,-1]) # close to col_both?



    cfg['hw']['adjust'] =  visual.Circle(win = cfg['hw']['win'],
                                        radius = .5,
                                        edges=100,
                                        lineWidth=0,
                                        fillColor=[-1,-1,1])

    cfg['hw']['fixed'] = visual.Circle(win = cfg['hw']['win'],
                                        radius = .5,
                                        edges=100,
                                        lineWidth=0,
                                        fillColor=[1,-1,-1])

    cfg['hw']['corner'] = visual.Circle(win = cfg['hw']['win'],
                                        radius = .5,
                                        edges=100,
                                        lineWidth=0,
                                        fillColor=[-1,.5,-1])


    cfg['hw']['abort'] = visual.Rect(win = cfg['hw']['win'],
                                     size = [1,1],
                                     lineWidth=5,
                                     lineColor=[1,-1,1],
                                     fillColor=None,
                                     # closeShape?
                                     ori=45)

    cfg['hw']['text'] = visual.TextStim(win=cfg['hw']['win'],
                                        text='',
                                        pos=[0,0]
                                        )


    cfg['hw']['diamond'] = visual.ShapeStim(cfg['hw']['win'], 
                                pos = [0,0],
                                vertices=[[[0,.6],[.6,0],[0,-.6],[-.6,0],[0,.6]],[[0,.4],[.4,0],[0,-.4],[-.4,0],[0,.4]]], 
                                lineWidth = 0, 
                                units = 'deg', 
                                size = (1, 1), # might be too small?
                                closeShape = True, 
                                lineColor = None,
                                fillColor=[1,-1,1]) # close to col_both?

    cfg['hw']['mouse'] = event.Mouse(visible=False, win=cfg['hw']['win']) # invisible !!

    return(cfg)


def getTasks(cfg):

    if cfg['expno']==1:

        condictionary = [

                         # crossing a meridian:

                         # offset: +0.5

                         {'test':'up-right-vertical',     'corner':[ 7.5,  7.5], 'fixed':[-7.5,  7.5], 'adjust':[ 7.5, -7.5], 'coord':1, 'offset':0.5},
                         {'test':'up-right-horizontal',   'corner':[ 7.5,  7.5], 'fixed':[ 7.5, -7.5], 'adjust':[-7.5,  7.5], 'coord':0, 'offset':0.5},

                         {'test':'up-left-vertical',      'corner':[-7.5,  7.5], 'fixed':[ 7.5,  7.5], 'adjust':[-7.5, -7.5], 'coord':1, 'offset':0.5},
                         {'test':'up-left-horizontal',    'corner':[-7.5,  7.5], 'fixed':[-7.5, -7.5], 'adjust':[ 7.5,  7.5], 'coord':0, 'offset':0.5},

                         {'test':'down-right-vertical',   'corner':[ 7.5, -7.5], 'fixed':[-7.5, -7.5], 'adjust':[ 7.5,  7.5], 'coord':1, 'offset':0.5},
                         {'test':'down-right-horizontal', 'corner':[ 7.5, -7.5], 'fixed':[ 7.5,  7.5], 'adjust':[-7.5, -7.5], 'coord':0, 'offset':0.5},

                         {'test':'down-left-vertical',    'corner':[-7.5, -7.5], 'fixed':[ 7.5, -7.5], 'adjust':[-7.5,  7.5], 'coord':1, 'offset':0.5},
                         {'test':'down-left-horizontal',  'corner':[-7.5, -7.5], 'fixed':[-7.5,  7.5], 'adjust':[ 7.5, -7.5], 'coord':0, 'offset':0.5},

                         # offset: -0.5

                         {'test':'up-right-vertical',     'corner':[ 7.5,  7.5], 'fixed':[-7.5,  7.5], 'adjust':[ 7.5, -7.5], 'coord':1, 'offset':-0.5},
                         {'test':'up-right-horizontal',   'corner':[ 7.5,  7.5], 'fixed':[ 7.5, -7.5], 'adjust':[-7.5,  7.5], 'coord':0, 'offset':-0.5},

                         {'test':'up-left-vertical',      'corner':[-7.5,  7.5], 'fixed':[ 7.5,  7.5], 'adjust':[-7.5, -7.5], 'coord':1, 'offset':-0.5},
                         {'test':'up-left-horizontal',    'corner':[-7.5,  7.5], 'fixed':[-7.5, -7.5], 'adjust':[ 7.5,  7.5], 'coord':0, 'offset':-0.5},

                         {'test':'down-right-vertical',   'corner':[ 7.5, -7.5], 'fixed':[-7.5, -7.5], 'adjust':[ 7.5,  7.5], 'coord':1, 'offset':-0.5},
                         {'test':'down-right-horizontal', 'corner':[ 7.5, -7.5], 'fixed':[ 7.5,  7.5], 'adjust':[-7.5, -7.5], 'coord':0, 'offset':-0.5},

                         {'test':'down-left-vertical',    'corner':[-7.5, -7.5], 'fixed':[ 7.5, -7.5], 'adjust':[-7.5,  7.5], 'coord':1, 'offset':-0.5},
                         {'test':'down-left-horizontal',  'corner':[-7.5, -7.5], 'fixed':[-7.5,  7.5], 'adjust':[ 7.5, -7.5], 'coord':0, 'offset':-0.5},


                         # offset: +1.5

                         {'test':'up-right-vertical',     'corner':[ 7.5,  7.5], 'fixed':[-7.5,  7.5], 'adjust':[ 7.5, -7.5], 'coord':1, 'offset':1.5},
                         {'test':'up-right-horizontal',   'corner':[ 7.5,  7.5], 'fixed':[ 7.5, -7.5], 'adjust':[-7.5,  7.5], 'coord':0, 'offset':1.5},

                         {'test':'up-left-vertical',      'corner':[-7.5,  7.5], 'fixed':[ 7.5,  7.5], 'adjust':[-7.5, -7.5], 'coord':1, 'offset':1.5},
                         {'test':'up-left-horizontal',    'corner':[-7.5,  7.5], 'fixed':[-7.5, -7.5], 'adjust':[ 7.5,  7.5], 'coord':0, 'offset':1.5},

                         {'test':'down-right-vertical',   'corner':[ 7.5, -7.5], 'fixed':[-7.5, -7.5], 'adjust':[ 7.5,  7.5], 'coord':1, 'offset':1.5},
                         {'test':'down-right-horizontal', 'corner':[ 7.5, -7.5], 'fixed':[ 7.5,  7.5], 'adjust':[-7.5, -7.5], 'coord':0, 'offset':1.5},

                         {'test':'down-left-vertical',    'corner':[-7.5, -7.5], 'fixed':[ 7.5, -7.5], 'adjust':[-7.5,  7.5], 'coord':1, 'offset':1.5},
                         {'test':'down-left-horizontal',  'corner':[-7.5, -7.5], 'fixed':[-7.5,  7.5], 'adjust':[ 7.5, -7.5], 'coord':0, 'offset':1.5},


                         # offset: -1.5

                         {'test':'up-right-vertical',     'corner':[ 7.5,  7.5], 'fixed':[-7.5,  7.5], 'adjust':[ 7.5, -7.5], 'coord':1, 'offset':-1.5},
                         {'test':'up-right-horizontal',   'corner':[ 7.5,  7.5], 'fixed':[ 7.5, -7.5], 'adjust':[-7.5,  7.5], 'coord':0, 'offset':-1.5},

                         {'test':'up-left-vertical',      'corner':[-7.5,  7.5], 'fixed':[ 7.5,  7.5], 'adjust':[-7.5, -7.5], 'coord':1, 'offset':-1.5},
                         {'test':'up-left-horizontal',    'corner':[-7.5,  7.5], 'fixed':[-7.5, -7.5], 'adjust':[ 7.5,  7.5], 'coord':0, 'offset':-1.5},

                         {'test':'down-right-vertical',   'corner':[ 7.5, -7.5], 'fixed':[-7.5, -7.5], 'adjust':[ 7.5,  7.5], 'coord':1, 'offset':-1.5},
                         {'test':'down-right-horizontal', 'corner':[ 7.5, -7.5], 'fixed':[ 7.5,  7.5], 'adjust':[-7.5, -7.5], 'coord':0, 'offset':-1.5},

                         {'test':'down-left-vertical',    'corner':[-7.5, -7.5], 'fixed':[ 7.5, -7.5], 'adjust':[-7.5,  7.5], 'coord':1, 'offset':-1.5},
                         {'test':'down-left-horizontal',  'corner':[-7.5, -7.5], 'fixed':[-7.5,  7.5], 'adjust':[ 7.5, -7.5], 'coord':0, 'offset':-1.5}

                         ]

        return( dictToBlockTrials(cfg=cfg, condictionary=condictionary, nblocks=1, nrepetitions=1, shuffle=True) )


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

def exportData(cfg):

    responses = cfg['responses']

    # collect names of data:
    columnnames = []
    for response in responses:
        rks = list(response.keys())
        addthese = np.nonzero([not(rk in columnnames) for rk in rks])[0]
        # [x+1 if x >= 45 else x+5 for x in l]
        [columnnames.append(rks[idx]) for idx in range(len(addthese))]

    # make dict with columnnames as keys that are all empty lists:
    respdict = dict.fromkeys(columnnames)
    columnnames = list(respdict)
    for rk in respdict.keys():
        respdict[rk] = []

    #respdict = {}
    #for colname in columnnames:
    #    respdict[colname] = []

    # go through responses and collect all data into the dictionary:
    for response in responses:
        for colname in columnnames:
            if colname in list(response.keys()):
                respdict[colname] += [response[colname]]
            else:
                respdict[colname] += ['']

    #for rk in respdict.keys():
    #    print([rk, len(respdict[rk])])

    pd.DataFrame(respdict).to_csv('%sresponses.csv'%(cfg['datadir']), index=False)

    print('data exported to csv')

    return(cfg)


def runTasks(cfg):

    cfg['responses'] = []

    if not('currentblock' in cfg):
        cfg['currentblock'] = 0
    if not('currenttrial' in cfg):
        cfg['currenttrial'] = 0

    # if cfg['eyetracking']:
    #     cfg['hw']['tracker'].openfile()
    #     cfg['hw']['tracker'].startcollecting()
        
    while cfg['currentblock'] < len(cfg['blocks']):

        # do the trials:
        cfg['currenttrial'] = 0

        showInstruction(cfg)

        # if cfg['eyetracking']:
        #     cfg['hw']['tracker'].comment('block %d/%d'%(cfg['currentblock']+1, len(cfg['blocks'])))

        # after instructions, calibrate:
        if cfg['eyetracking']:
            # cfg['hw']['tracker'].comment('calibration start')
            cfg['hw']['tracker'].calibrate()
            # cfg['hw']['tracker'].comment('calibration done')

        while cfg['currenttrial'] < len(cfg['blocks'][cfg['currentblock']]['trialtypes']):
            
            # if cfg['eyetracking']:
                # cfg['hw']['tracker'].comment('trial %d'%(cfg['currenttrial']))


            # print([cfg['currenttrial'], len(cfg['blocks'][cfg['currentblock']]['trialtypes'])])

            # trialtype = cfg['blocks'][cfg['currentblock']]['trialtypes'][cfg['currenttrial']]
            # trialdict = cfg['conditions'][trialtype]

            print('block %d/%d; trial %d/%d\n'%(cfg['currentblock']+1, len(cfg['blocks']),cfg['currenttrial']+1, len(cfg['blocks'][cfg['currentblock']]['trialtypes'])))

            cfg = doTrial(cfg)
            saveCfg(cfg)

            cfg['currenttrial'] += 1

        cfg['currentblock'] += 1

    if cfg['eyetracking']:
        cfg['hw']['tracker'].closefile()
    
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

    # filefolder = cfg['datadir']
    # filename = '%s_exp%d'%(cfg['ID'],cfg['expno'])

    # do not store any files anywhere:
    filefolder = None
    filename = None

    colors = {'back' : [ 0, 0, 0],
              'both' : [-1,-1,-1]} # only for EyeLink
    
    ET = EyeTracker( tracker           = 'livetrack',
                     trackEyes         = trackEyes,
                     fixationWindow    = 2.0,                  # generous
                     minFixDur         = 0.2,
                     fixTimeout        = 3.0,
                     psychopyWindow    = cfg['hw']['win'],
                     filefolder        = filefolder,
                     filename          = filename,
                     samplemode        = 'average',
                     calibrationpoints = 9,
                     colors            = colors ) # only for EyeLink

    # ET.initialize(calibrationPoints = np.array([[0,0],   [6,0],[0,6],[-6,0],[0,-6],  [12,12],[-12,12],[-12,-12],[12,-12]  ]) )

    ET.initialize(calibrationPoints = np.array([[0,0],   [6,0],[0,6],[-6,0],[0,-6]  ]) )

    cfg['hw']['tracker'] = ET

    return(cfg)



def doTrial(cfg):

    trialtype = cfg['blocks'][cfg['currentblock']]['trialtypes'][cfg['currenttrial']]
    # trialdict = cfg['conditions'][trialtype]
    trialdict = copy.deepcopy(cfg['conditions'][trialtype])

    # if cfg['eyetracking']:
    #     cfg['hw']['tracker'].comment('block %d',cfg['currentblock'])
    #     cfg['hw']['tracker'].comment('trial %d',cfg['currenttrial'])

    # here the magic happens ! ! ! ! ! ! ! ! !

    mouse_scale = 1.5

    # {'test':'up-right-vertical',     'corner':[ 7.5,  7.5], 'fixed':[-7.5,  7.5], 'adjust':[ 7.5, -7.5], 'coord':1, 'offset':0.5}
    # unpack the expected variables from the trial-dictionary:

    if 'test' in trialdict.keys():
        test = trialdict['test']
    else:
        test = 'undeclared'
        trialdict['test'] = test

    if 'corner' in trialdict.keys():
        corner = trialdict['corner']
        cfg['hw']['corner'].pos = corner
        drawCorner = True
    else:
        drawCorner = False
        trialdict['corner'] = [None, None]
    
    if 'fixed' in trialdict.keys():
        fixed = trialdict['fixed']
        cfg['hw']['fixed'].pos = fixed
        drawFixed = True
    else:
        drawFixed = False
        trialdict['fixed'] = [None, None]

    if 'offset' in trialdict.keys():
        offset = trialdict['offset']
    else:
        offset = None
        trialdict['offset'] = offset

    if 'coord' in trialdict.keys():
        coord = trialdict['coord']
        adjustPos = True
    else:
        coord = None
        trialdict['coord'] = coord
        adjustPos = False

    if 'adjust' in trialdict.keys():
        adjust = trialdict['adjust']
        # only works if we have corner and adjust positions, and offset and coord are set:
        if all([coord != None, offset != None, corner[0] == None, adjust[0] == None]):

            # check adjustment direction
            direct = np.sign(diff([corner[coord],adjust[coord]])[0])
            adjust[coord] += (direct * offset)
        cfg['hw']['adjust'].pos = adjust
        drawAdjust = True
    else:
        # do we even do the trial? no response would make sense...
        drawAdjust = False
        trialdict['adjust'] = [None, None]
    
    jitter = random.sample([-1.5,-1,-.5,.5,1,1.5])[0]
    jitter = [jitter * np.sign(x) for x in corner]
    cfg['hw']['fixation'].pos = jitter


    # MOUSE POS SHOULD BE SET TO [0,0]
    cfg['hw']['mouse'].setPos([0,0])


    waiting_for_response = True
    event.clearEvents(eventType='keyboard')

    while waiting_for_response:

        if cfg['eyetracking']:
            if cfg['hw']['tracker'].gazeInFixationWindow(fixloc=jitter):
                drawStimuli = True
            else:
                drawStimuli = False
        else:
            drawStimuli = True

        # read out mouse position, and use for adjusting the adjustable dot position:
        if adjustPos:
            adjust_pos = adjust
            adjust_pos[coord] = (cfg['hw']['mouse'].getPos()[coord] / mouse_scale)
            cfg['hw']['adjust'].pos = adjust_pos

        if drawStimuli:
            # draw available stimuli:
            if (time.time() % 1) > 0.2:
                if drawCorner:
                    cfg['hw']['corner'].draw()
                if drawFixed:
                    cfg['hw']['fixed'].draw()
                if drawAdjust:
                    cfg['hw']['adjust'].draw()

        cfg['hw']['fixation'].draw()
        cfg['hw']['win'].flip()

        k = event.getKeys(['space','q','0'])
        if k:
            if 'q' in k:
                # abort trial?
                # quit experiment!
                # maybe not...
                pass
            if 'space' in k:
                waiting_for_response = False
            if '0' in k:
                if cfg['eyetracking']:
                    # recalibrate:
                    cfg['hw']['tracker'].calibrate()

    

    response                  = copy.deepcopy(trialdict)
    response['final_adjust']  = cfg['hw']['adjust'].pos
    response['horizontal_d']  = abs(cfg['hw']['corner'].pos[0] - cfg['hw']['adjust'].pos[0])
    response['vertical_d']    = abs(cfg['hw']['corner'].pos[1] - cfg['hw']['adjust'].pos[1])


    cfg['responses'] += [response]





    # dont forget to STORE RESPONSES ! ! ! ! ! ! ! ! ! ! ! !


    return(cfg)



def cleanExit(cfg):

    cfg['expfinish'] = time.time()

    saveCfg(cfg)

    print('cfg stored as json')

    if cfg['eyetracking']:
        cfg['hw']['tracker'].comment('end of run')
        cfg['hw']['tracker'].stopcollecting()
        cfg['hw']['tracker'].closefile()
        cfg['hw']['tracker'].shutdown()

        del cfg['hw']['tracker'] # is this what we want?

    cfg['hw']['win'].close()

    return(cfg)

def saveCfg(cfg):

    print('skipping saving cfg for now...')
    # scfg = copy.copy(cfg)
    # del scfg['hw']

    # entries = scfg.keys()
    # for entry in entries:
    #     print(scfg[entry])

    # with open('%scfg.json'%(cfg['datadir']), 'w') as fp:
    #     json.dump(scfg, fp,  indent=4)

