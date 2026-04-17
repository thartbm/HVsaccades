#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Colour calibration for monocular/colour glasses presentation
Blind spot mapping
TWCF IIT vs PP experiment 2a
"""

import sys, os
sys.path.append(os.path.join('..', 'EyeTracking'))
from EyeTracking import localizeSetup, EyeTracker

import math
import time
import random
import copy
import os
import numpy as np
from glob import glob


from psychopy import core, visual, event, gui, monitors, data
from psychopy.tools.coordinatetools import pol2cart, cart2pol
from psychopy.hardware import keyboard
from pyglet.window import key


def doColorCalibration(ID=None, task=None, location=None):

    expInfo = {}
    askQuestions = False
    if ID == None:
        ## files
        expInfo['ID'] = ''
        askQuestions = True
    if task == None:
        expInfo['task'] = ['distHorizontal', 'distBinocular', 'distScaled', 'distCentred', 'distRotated','distUpturned','distUpshifted','distAsynchronous','distScaledAsynchronous','distScaledAsynchronousOFS','distUpScaledAsynchronous','distAsynchronousNAM', 'distBinocHorizontal']
        askQuestions = True
    # if location == None:
    #     expInfo['location'] = ['glasgow', 'toronto']
    #     askQuestions = True

    if askQuestions:
        dlg = gui.DlgFromDict(expInfo, title='Infos')

    if ID == None:
        ID = expInfo['ID']
    if task == None:
        task = expInfo['task']
    # if location == None:
    #     location = expInfo[]

    ## path
    data_path = "../data/%s/color/"%(task)
    os.makedirs(data_path, exist_ok=True)

    filename = ID.lower() + '_col_cal_'

    glasses = 'RG' # NO CHOICE !


    # colors will come from the localizeSetup function, depending on things

    # if glasses == 'RG':
    #     back_col   = [ 0.5, 0.5,  -1.0]
    #     red_col    = [0.5, -1.0,  -1.0]
    #     blue_col   = [ -1.0, 0.5, -1.0]
    # elif glasses == 'RB':
    #     back_col   = [ 0.5, -1.0,  0.5]
    #     red_col    = [ 0.5, -1.0, -1.0] #Flipped back 
    #     blue_col   = [-1.0, -1.0,  0.5] 


    track_eyes = 'none'    # NO CHOICE !
    trackEyes = [False,False]

    # need location
    if location == None:
        if os.sys.platform == 'linux':
            location = 'toronto'
        else:
            location = 'glasgow'

    # filefoder needs to be specified? maybe not for color calibration? no eye-tracking files will be written...
    # not sending colors to localize setup, since we're still determining them here: use defaults for now!
    setup = localizeSetup(location=location, glasses=glasses, trackEyes=trackEyes, filefolder=None, filename=None, task=task, ID=ID) # data path is for the mapping data, not the eye-tracker data!

    cfg = {}
    cfg['hw'] = setup

    # since these values will be changed and stored in a file, let's make them available locally:
    back_col = cfg['hw']['colors']['back'] # technically, this one will not need to be changed, it should be a constant?
    red_col  = cfg['hw']['colors']['red']
    blue_col = cfg['hw']['colors']['blue'] # actually green?

    print(cfg['hw']['colors'])

    # print(cfg['hw']['win'].monitor.getGammaGrid())
    # print(cfg['hw']['win'].color)


    cfg['hw']['win'].viewPos = [0,0]


    # add pyglet keyboard stuff:
    pyg_keyboard = key.KeyStateHandler()
    cfg['hw']['win'].winHandle.push_handlers(pyg_keyboard)

    dot_blue_left  = visual.Circle(cfg['hw']['win'], radius = 2.5, pos = [-7, 7], fillColor = cfg['hw']['colors']['blue'], colorSpace = 'rgb', lineColor = None)
    dot_red_left   = visual.Circle(cfg['hw']['win'], radius = 2.5, pos = [-7,-7], fillColor = cfg['hw']['colors']['red'],  colorSpace = 'rgb', lineColor = None)
    dot_both_left  = visual.Circle(cfg['hw']['win'], radius = 2.5, pos = [ 0,-9], fillColor = cfg['hw']['colors']['back'], colorSpace = 'rgb', lineColor = None)

    dot_blue_right = visual.Circle(cfg['hw']['win'], radius = 2.5, pos = [ 7,-7], fillColor = cfg['hw']['colors']['blue'], colorSpace = 'rgb', lineColor = None)
    dot_red_right  = visual.Circle(cfg['hw']['win'], radius = 2.5, pos = [ 7, 7], fillColor = cfg['hw']['colors']['red'],  colorSpace = 'rgb', lineColor = None)
    dot_both_right = visual.Circle(cfg['hw']['win'], radius = 2.5, pos = [ 0, 9], fillColor = cfg['hw']['colors']['back'], colorSpace = 'rgb', lineColor = None)

    # fixation = visual.ShapeStim(cfg['hw']['win'], vertices = ((0, -1), (0, 1), (0,0), (-1, 0), (1, 0)), lineWidth = 5, units = 'deg', size = (1, 1), closeShape = False, lineColor = 'white')


    step = 0.0015 # RGB color space has 256 values so the step should be 2/256, but that moves too fast

    frameN = 0
    while 1:

        # k = event.getKeys(['left', 'right', 'up', 'down' ,'escape', 'space', '1', 'q'])
        k = event.getKeys(['escape', 'space', 'q'])

        if k:
            # if k[0] in ['q']:
            #     calibration_triggered
            if k[0] in ['space','escape']:
                break

            # if k[0] == 'left':
            #     red_col[2]  = max(-1, red_col[2]  - step)
            # if k[0] == 'right':
            #     red_col[2]  = min( 1, red_col[2]  + step)
            # if k[0] == 'up':
            #     blue_col[0] = min( 1, blue_col[0] + step)
            # if k[0] == 'down':
            #     blue_col[0] = max(-1, blue_col[0] - step)

            if k[0] == '1':
                print("red: " + str(red_col))
                print("blue: " + str(blue_col))


        # check fixation
        allow_calibration = True

        # if cfg['hw']['tracker'].gazeInFixationWindow():
        #     allow_calibration = True
        # else:
        #     allow_calibration = False



        if allow_calibration:
            if glasses == 'RG':
                if pyg_keyboard[key.LEFT]:
                    red_col[0]  = max(-1, red_col[0]  - step)
                if pyg_keyboard[key.RIGHT]:
                    red_col[0]  = min( 1, red_col[0]  + step)
                if pyg_keyboard[key.UP]:
                    blue_col[1] = min( 1, blue_col[1] + step)
                if pyg_keyboard[key.DOWN]:
                    blue_col[1] = max(-1, blue_col[1] - step)
                if pyg_keyboard[key.R]:
                    print('threshold found', red_col)
                if pyg_keyboard[key.B]:
                    print('threshold found', blue_col)
            elif glasses == 'RB':
                if pyg_keyboard[key.LEFT]:
                    red_col[0]  = max(-1, red_col[0]  - step)
                if pyg_keyboard[key.RIGHT]:
                    red_col[0]  = min( 1, red_col[0]  + step)
                if pyg_keyboard[key.UP]:
                    blue_col[2] = min( 1, blue_col[2] + step)
                if pyg_keyboard[key.DOWN]:
                    blue_col[2] = max(-1, blue_col[2] - step)


        dot_red_left.fillColor   = red_col
        dot_red_right.fillColor  = red_col
        dot_blue_left.fillColor  = blue_col
        dot_blue_right.fillColor = blue_col

        if frameN >= 0 and frameN < 12:
            dot_both_left.fillColor   = red_col
            dot_both_right.fillColor  = red_col
        else:
            dot_both_left.fillColor  = blue_col
            dot_both_right.fillColor = blue_col

        frameN+=1

        if frameN >23:
            frameN = 0

        # fixation.draw()
        cfg['hw']['fixation'].draw()
        # dot_both_left.draw()
        dot_blue_left.draw()
        dot_red_left.draw()
        # dot_both_right.draw()
        dot_blue_right.draw()
        dot_red_right.draw()

        event.clearEvents(eventType='mouse')
        event.clearEvents(eventType='keyboard')

        cfg['hw']['win'].flip()


        # if calibration_triggered:

        #     cfg['hw']['tracker'].stopcollecting()

        #     cfg['hw']['tracker'].calibrate()

        #     cfg['hw']['tracker'].startcollecting()

        #     calibration_triggered = False

    # open file here:
    x = 1
    while (filename + str(x) + '.txt') in os.listdir(data_path): x += 1
    respFile = open(data_path + filename + str(x) + '.txt','w')
    # write data to file:
    respFile.write('background:\t[{:.8f},{:.8f},{:.8f}]\nred:\t[{:.8f},{:.8f},{:.8f}]\ngreen:\t[{:.8f},{:.8f},{:.8f}]'.format( \
    back_col[0], back_col[1], back_col[2], \
    red_col[0],  red_col[1],  red_col[2],  \
    blue_col[0], blue_col[1], blue_col[2]))
    respFile.close()


    # to CLI:
    print("background: " + str(back_col))
    print("red: " + str(red_col))
    print("blue: " + str(blue_col))

    # cfg['hw']['tracker'].stopcollecting()
    # cfg['hw']['tracker'].closefile()
    cfg['hw']['tracker'].shutdown()
    cfg['hw']['win'].close() # should be after tracker shutdown, since tracker may use the window still...









def doBlindSpotMapping(ID=None,task=None,location=None,offset=[0,0]):
    
    askQuestions = False
    expInfo = {}
    if ID == None:
        ## files
        expInfo['ID'] = ''
        askQuestions = True
    if task == None:
        expInfo['task'] = ['distHorizontal', 'distBinocular', 'distScaled', 'distCentred', 'distRotated','distUpturned','distUpshifted','distAsynchronous','distScaledAsynchronous','distScaledAsynchronousOFS','distUpScaledAsynchronous','distAsynchronousNAM', 'distBinocHorizontal']
        askQuestions = True
    # if hemifield == None:
    #     expInfo['hemifield'] = ['left','right']

    if askQuestions:
        dlg = gui.DlgFromDict(expInfo, title='Infos')

    if ID == None:
        ID = expInfo['ID']
    if task == None:
        task = expInfo['task']
    # if hemifield == None:
    #     hemifield = expInfo['hemifield']

    ## path
    data_path = "../data/%s/mapping/"%(task)
    os.makedirs(data_path, exist_ok=True)

    step = .25

    # # col_file = open(glob(main_path + 'mapping_data/' + ID + '_col_cal*.txt')[-1],'r')
    # col_file = open(glob('../data/' + task + '/color/' + ID + '_col_cal*.txt')[-1],'r')
    # col_param = col_file.read().replace('\t','\n').split('\n')
    # col_file.close()
    # col_left  = eval(col_param[3])
    # col_right = eval(col_param[5])
    # col_ipsi  = eval(col_param[3]) if hemifield == 'left' else eval(col_param[5]) # left or right
    # col_cont  = eval(col_param[5]) if hemifield == 'left' else eval(col_param[3]) # right or left
    # # col_both = [-0.7, -0.7, -0.7] # now dependent on calibrated colors:
    # col_both = [eval(col_param[3])[1], eval(col_param[5])[0], -1]
    # col_back = [ 0.5, 0.5,  -1.0] # should this come from setupLocalization?

    # colors = { 'left'   : col_left, 
    #            'right'  : col_right,
    #            'both'   : col_both,
    #            'ipsi'   : col_ipsi,
    #            'cont'   : col_cont  } 


    if location == None:
        if os.sys.platform == 'linux':
            location = 'toronto'
        else:
            location = 'glasgow'

    if location == 'toronto':
        step = .01

    print(location)
    print(step)

    glasses = 'RG'
    trackEyes = [True, True]

    setup = localizeSetup(location=location, glasses=glasses, trackEyes=trackEyes, filefolder=None, filename=None, task=task, ID=ID) # data path is for the mapping data, not the eye-tracker data!
    # setup = localizeSetup(location=location, glasses=glasses, trackEyes=trackEyes, filefolder=None, filename=None, task=task, ID=ID, noEyeTracker=True) # data path is for the mapping data, not the eye-tracker data!
    print(setup['paths'])

    colors = setup['colors']

    print(colors)

    # if hemifield == 'left':
    #     colors['ipsi'], colors['contra'] = colors['left'], colors['right']
    # if hemifield == 'right':
    #     colors['ipsi'], colors['contra'] = colors['right'], colors['left']

    cfg = {}
    cfg['hw'] = setup

    cfg['hw']['win'].viewPos = offset

    pyg_keyboard = key.KeyStateHandler()
    cfg['hw']['win'].winHandle.push_handlers(pyg_keyboard)

    if location != 'toronto':
        # initialization should've already been done for the case of Toronto?
        print('not toronto?')
        # cfg['hw']['tracker'].initialize()
    
    # cfg['hw']['tracker'].calibrate()
    # cfg['hw']['tracker'].startcollecting()
    
    # print('tracking...')

    fixation_yes = setup['fixation']
    fixation_no  = setup['fixation_x']

    cfg['hw']['fusion']['hi'].rows = 7
    cfg['hw']['fusion']['hi'].columns = 3
    cfg['hw']['fusion']['lo'].rows = 7
    cfg['hw']['fusion']['lo'].columns = 3


    if offset[1] != 0:

        cfg['hw']['fusion']['lo'].pos =  [cfg['hw']['fusion']['lo'].pos[0], cfg['hw']['fusion']['lo'].pos[1] + (offset[1]/2)]
        cfg['hw']['fusion']['lo'].rows = int(max(1, round(cfg['hw']['fusion']['lo'].rows + (offset[1]/2))))

        cfg['hw']['fusion']['hi'].pos =  [cfg['hw']['fusion']['hi'].pos[0], cfg['hw']['fusion']['hi'].pos[1] + (offset[1]/2)]
        cfg['hw']['fusion']['hi'].rows = int(max(1, round(cfg['hw']['fusion']['hi'].rows - (offset[1]/2))))

    cfg['hw']['tracker'].startcollecting()

    for hemifield in ['left', 'right']:

        abort = False

        if hemifield == 'left':
            colors['ipsi'], colors['contra'] = colors['left'], colors['right']
            filename = ID.lower() + '_LH_blindspot_'
            # win = visual.Window([1920,1080],allowGUI=True, monitor='ccni', units='deg', viewPos = [0,0], fullscr = True)
            # win = visual.Window(resolution, allowGUI=True, monitor=mymonitor, units='deg', viewPos = [0,0], fullscr=True, screen=1)
            point = visual.Circle(cfg['hw']['win'], size = [1,1], pos = [-7,-1], fillColor=colors['left'], lineColor = None, units='deg')
            if task == 'distUpScaledAsynchronous':
                cfg['hw']['win'].viewPos = [10,0]
                # cfg['hw']['fusion']['lo'].pos = [-10,-7] # does this even make sense? should just be the old position...
                # cfg['hw']['fusion']['hi'].pos = [-10,7]
        else:
            colors['ipsi'], colors['contra'] = colors['right'], colors['left']
            filename = ID.lower() + '_RH_blindspot_'
            # win = visual.Window([1920,1080],allowGUI=True, monitor='ccni', units='deg', viewPos = [0,0], fullscr = True)
            # win = visual.Window(resolution, allowGUI=True, monitor=mymonitor, units='deg', viewPos = [0,0], fullscr=True, screen=1)
            point = visual.Circle(cfg['hw']['win'], size = [1,1], pos = [7,-1], fillColor=colors['right'], lineColor = None, units='deg')
            if task == 'distUpScaledAsynchronous':
                cfg['hw']['win'].viewPos = [-10,0]
                # cfg['hw']['fusion']['lo'].pos = [10,-7]
                # cfg['hw']['fusion']['hi'].pos = [10,7]

        # point.fillColor = [-1,-1,-1]
        # print(point.size)
        
        cfg['hw']['fusion']['hi'].resetProperties()
        cfg['hw']['fusion']['lo'].resetProperties()

        cfg['hw']['tracker'].calibrate()
        # cfg['hw']['tracker'].startcollecting()


        # check what the file should be for the participant:
        x = 1
        while (filename + str(x) + '.txt') in os.listdir(data_path): x += 1
        

        cfg['hw']['win'].mouseVisible = False
        # fixation_yes = visual.ShapeStim(cfg['hw']['win'], vertices = ((0, -2), (0, 2), (0,0), (-2, 0), (2, 0)), lineWidth = 2, units = 'pix', size = (10, 10), closeShape = False, lineColor = colors['both'])
        # fixation_no = visual.ShapeStim(cfg['hw']['win'], vertices = ((0, -2), (0, 2), (0,0), (-2, 0), (2, 0)), lineWidth = 2, units = 'pix', size = (10, 10), closeShape = False, lineColor = colors['both'], ori = -45)
        fixation = fixation_yes
        abort = False

        fixation.draw()
        point.draw()
        cfg['hw']['win'].flip()

        while 1:
            # k = event.getKeys(['up', 'down', 'left', 'right', 'q', 'w', 'a', 's', 'space', 'escape', '0'])
            k = event.getKeys(['space', 'escape', '0', 'insert'])

            if k:
                if 'escape' in k:
                    abort = True
                    break

                if 'space' in k:
                    break
                if pyg_keyboard[key.NUM_INSERT]:
                    break

                if '0' in k:
                    # cfg['hw']['tracker'].stopcollecting() # do we even have to stop/start collecting?
                    cfg['hw']['tracker'].calibrate()
                    # cfg['hw']['tracker'].startcollecting()

            if cfg['hw']['tracker'].gazeInFixationWindow():
                fixation = fixation_yes
                
                if pyg_keyboard[key.UP]:
                    point.pos += [ 0, step]
                if pyg_keyboard[key.DOWN]:
                    point.pos += [ 0,-step]
                if pyg_keyboard[key.LEFT]:
                    point.pos += [-step, 0]
                if pyg_keyboard[key.RIGHT]:
                    point.pos += [ step, 0]

                if pyg_keyboard[key.Q]:
                    point.size += [step,0]
                if pyg_keyboard[key.W]:
                    point.size = [max(step, point.size[0] - step), point.size[1]]
                if pyg_keyboard[key.A]:
                    point.size += [0, step]
                if pyg_keyboard[key.S]:
                    point.size = [point.size[0], max(step, point.size[1] - step)]

                if pyg_keyboard[key.NUM_UP]:
                    point.pos += [ 0, step]
                if pyg_keyboard[key.NUM_DOWN]:
                    point.pos += [ 0,-step]
                if pyg_keyboard[key.NUM_LEFT]:
                    point.pos += [-step, 0]
                if pyg_keyboard[key.NUM_RIGHT]:
                    point.pos += [ step, 0]

                if pyg_keyboard[key.NUM_HOME]:
                    point.size += [step,0]
                if pyg_keyboard[key.NUM_PAGE_UP]:
                    point.size = [max(step, point.size[0] - step), point.size[1]]
                if pyg_keyboard[key.NUM_END]:
                    point.size += [0, step]
                if pyg_keyboard[key.NUM_PAGE_DOWN]:
                    point.size = [point.size[0], max(step, point.size[1] - step)]
            else:
                fixation = fixation_no
                
            # if anything, fusion patterns should be below other stimuli:
            cfg['hw']['fusion']['hi'].draw()
            cfg['hw']['fusion']['lo'].draw()
            fixation.draw()
            if ((time.time() % 1) > 0.4):
                point.draw()
            cfg['hw']['win'].flip()

            # print(point.pos)

        if not abort:
            cfg['hw']['fusion']['hi'].draw()
            cfg['hw']['fusion']['lo'].draw()
            fixation.draw()
            point.draw()
            
            cfg['hw']['win'].flip()
            cfg['hw']['win'].getMovieFrame()
            cfg['hw']['win'].saveMovieFrames(data_path + filename + str(x) + '.png')

            respFile = open(data_path + filename + str(x) + '.txt','w')
            respFile.write('position:\t[{:.2f},{:.2f}]\nsize:\t[{:.2f},{:.2f}]'.format(point.pos[0], point.pos[1],  point.size[0], point.size[1]))
            respFile.close()


    cfg['hw']['tracker'].stopcollecting()
    # close files here? there shouldn't be any...
    cfg['hw']['tracker'].shutdown()
    cfg['hw']['win'].close()