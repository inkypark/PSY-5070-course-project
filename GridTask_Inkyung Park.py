
###############GRID TASK FOR WISHFUL THINKING DRIFT DIFFUSION MODELING (shortened ver with 20 trials)#######################

######Import packages 
from __future__ import division
from psychopy import  gui, visual, event, core, data
from psychopy.visual import ShapeStim
from psychopy.hardware import keyboard

import math
import random
import trialSeq


from random import randrange


#######Initialize variables/ trial sequence
total_point = 0 #tracks total points earned from the task
accuracy = 0 #tracks overall accuracy of participant's predictions
kb= None
trial_prog = 1 #tracks trial progress (+1 after every trial)
block_prog = 1 #tracks block progress (+1 after every block)

trial_seq=trialSeq.GenerateRandTrialSeq()[0] #Generate trial sequences
block_done = trialSeq.GenerateRandTrialSeq()[1] #Calculate how many trials are included in a block
print(trial_seq)



#######Set Monitor Configuration
scr_width=1600 #Set screen width
scr_height=900 #Set screen height

win = visual.Window(
    size = (1600,900),fullscr=True, screen=2, 
    winType='pyglet', allowGUI=False, allowStencil=False,
    monitor='testMonitor', color='black', colorSpace='rgb',
    blendMode='avg', useFBO=True,  
    units='cm')
win.mouseVisible= False #hide the mouse



#######Set keyboard and outputfile
kb = keyboard.Keyboard() 
log_file = open('logfile.csv', 'a') #open log file



#######Open experiment setup prompt 
expName = 'DriftD Study 01'  
expPrompt = {'RP': '9999', 'RA initial': '9999', 'session': '9999', 'cond': '9999'} #Research Participant ID, Research Assitant initial, session # and condition

expPrompt['date'] = data.getDateStr()  # add a timestamp
expPrompt['expName'] = expName




#######Experiment settings (this is kept constant throughout data collection, may be changed in later versions of the studies)
respKeys = ['z', 'slash','escape','space'] #define available keys

trial_dur = 4 #Maximum duration of a trial 
sqr_fb_dur = .5 #duration for feedback presentation
fix_dur = .5 #duration for fixation cross presentation
critKey_pos = 'left'#the position of the key press that would indicate 'critical square'
grid_N = 20 #Should be always a multiple of 10
sqr_N = grid_N*grid_N #equals total number of squares

#calculates the position of the square that would indicate a left response (right key response can be calculated afterwards)
respKey_diag =  100 #position of the respKey squre (represented in the diagonal distance away from the screen corner) 
respKey_dist =  math.sqrt(0.5 * respKey_diag**2) #x and y value for the postion of the respKey squre (equidistant from x and y axis)
respKey_xpos =  -(scr_width/2) + respKey_dist
respKey_ypos =  -(scr_height/2) + respKey_dist



######Save Experiment info
expInfo = "Task,"+ expPrompt['expName'] +",RP,"+ expPrompt['RP']+ ",RA," +expPrompt['RA initial'] + ",cond," + expPrompt['cond'] +",date," + expPrompt['date'] + ",critKey," + critKey_pos



######Create function that draws a single square
#Inputs
#   sqrsz = integer. size of the single square in pixel
#   xpos = integer. x coordinate for the center of the single square 
#   ypos = integer. y coordinate for the center of the single square 
#   col = string. color of the square
#Output
#   single_square = a single square on window screen
def DrawSquares(sqrsz= 10, xpos=0, ypos=0, col='white'):
    global win
    
    single_square = visual.Rect(win, width=sqrsz, height=sqrsz, units='pix', lineWidth=1.5, lineColor='black', lineColorSpace='rgb', fillColor=col, 
            fillColorSpace='rgb', pos=(xpos, ypos), size=None, ori=0.0, opacity=1.0, contrast=1.0, autoDraw=False)
            
    return single_square



######Set coordinates to draw the grid (defines N x N square grid matrix coordinates)
#Inputs
#   scale = float. defines the scale of the grid size relative to the screen height
#   y = integer. value adjusting the position of the grid on the y axis (y=0 means that the grid is in the center of the screen)
#Output
#   temp_sqr = array of squares that are temporarily drawn to form a grid
#   sqr_size = size of the single square in pixel 
def SetGridParameters(scale = 2/3, y = 0):
    
    #Defines the size of the grid and single square (in pixel)
    grid_size = scr_height*scale
    sqr_size= grid_size/grid_N

    #Calculate the coordinate of the 1st square position (1st squre = squre on the top left corner) *postion=center
    y_adj = y #adjusts the y position of the grid
    xpos_sqr1 = -1* ((((grid_N/2)-1)*sqr_size) + (sqr_size/2))
    ypos_sqr1 = ((((grid_N/2)-1)*sqr_size) + (sqr_size/2))+y_adj

    #Initialize the list that will contain the rest of the squares' x, y coordinates
    xpos_list = [xpos_sqr1]
    ypos_list = [ypos_sqr1]
    
    #The loop creates all the x and y coordinates for the squares in the grid, and append them in xpos_list, ypos_list  
    for i in range(1,grid_N):
        x = xpos_sqr1+sqr_size*i
        xpos_list.append(x)
        y = ypos_sqr1-sqr_size*i
        ypos_list.append(y) 

    #Create temporary squares without color specification (This is not included in DrawGrids function because it slows down the generation of each grid sims across trials)
    temp_sqr = [[None for _ in range(grid_N)] for _ in range(grid_N)] #create GridN x GridN list of 'None's. Placeholder for squares 
    
    #Draw temporary squares that would consist a grid
    for i in range(0,grid_N):
        for m in range (0, grid_N):
            temp_sqr[i][m] = DrawSquares(sqrsz= sqr_size, xpos=xpos_list[m], ypos=ypos_list[i])
    
    return [temp_sqr,sqr_size]

temp_sqr = SetGridParameters()[0] #for main task
sqr_size = SetGridParameters()[1] #for main task
inst_temp_sqr = SetGridParameters(scale = 3/7, y =100)[0] #for the instructions (smaller in size)
inst_sqr_size = SetGridParameters(scale = 3/7, y =100)[1] #for the instructions (smaller in size)



#######Create function for generating grid color pattern 
#Inputs
#   crit_col = string. color of the critical square
#   neut_col = string. color of the neutral square
#   prob = float. proportion of critical square out of all squares
#Output
#   colorarray_temp = array that contains gridN x gridN number of color strings
def SetGridPattern(crit_col = 'darkred', neut_col = 'gray', prob = .5):
    
    ######Create random array for color strings
    crit_N = int(sqr_N*prob) #number of critical squares
    crit_list = [crit_col]*crit_N #create list that contains crit_N number of color strings
    neut_N = int(sqr_N*(1-prob)) #number of neutral patches, catches errors for miscalculations in the probs above 50% (for some reason that happens)
    if neut_N%2 == 0:
        neut_list = [neut_col]*neut_N
    elif neut_N%2 == 1:
        neut_list = [neut_col]*(neut_N+1)
    

    #######randomize the order of color strings in the array 
    colorarray_temp = crit_list+ neut_list
    random.shuffle(colorarray_temp)

    return colorarray_temp
    
inst_ca_pos = SetGridPattern() #for the instructions   
inst_ca_neg = SetGridPattern(crit_col ='darkblue')  #for the instructions




#######Create function for drwing the grid stim
#Inputs
#   opcty = integer. opacity of the grid_N
#   ca = array containing strings for square colors(determines the color pattern of the grid)
#   ts = array of squares that are temporarily drawn to form a grid
#Output
#   Grid stimuli
def DrawGrid(opcty=1, ca = ['white' for _ in range(grid_N*grid_N)], ts = temp_sqr):
        counter = 0
        for i in range(0,grid_N):
            for m in range (0, grid_N):
                #this will draw main grid in the center
                ts[i][m].fillColor = ca[counter]
                ts[i][m].opacity = opcty
                ts[i][m].draw()
                counter=counter+1



######Initialize the squares that would indicate the response keys  
#Inputs
#   cc= string. color of critical square
#   nc = string. color of neutral square
#Output
#   Two squares each one at the right and left corner to indicate the color associated with key response
def DrawRespKey(cc = 'darkred', nc = 'grey'):
    if critKey_pos == 'left':
        Lkey_square = DrawSquares(sqrsz= sqr_size, xpos= respKey_xpos, ypos= respKey_ypos, col=cc)
        Rkey_square = DrawSquares(sqrsz= sqr_size, xpos= -respKey_xpos, ypos= respKey_ypos, col=nc)
    else:
        Lkey_square = DrawSquares(sqrsz= sqr_size, xpos= respKey_xpos, ypos= respKey_ypos, col=nc)
        Rkey_square = DrawSquares(sqrsz= sqr_size, xpos= -respKey_xpos, ypos= respKey_ypos, col=cc)
    return [Lkey_square,Rkey_square]


#create text stimulus with preset values 
#input
#   txt = string. the content of the text
#   p = array of two integer. x,y coordinate for text stim
#   wrpw = integer determining wrapWidth 
#   b = boolean. bold text
#   a = string. text alignment (right, left, center)
#   v = string. text vertical anchoing (top, bottom, center)
def TextStimulus(txt = "", p = [0,0], h = 30, wrpW = 1400, b = True, a = "center", v = "center"):
    txtStim = visual.TextStim(win, text = txt, pos=p, color='white', units='pix', height=h, wrapWidth = wrpW, bold = b, alignText = a,anchorVert = v)
    txtStim.draw()
    

#Create 'space bar' text for the instruction
def PresentSpaceBar():
    TextStimulus(txt = "Please press the SPACE BAR to continue", p=[0,-370], b = True)


def Instruction1():
    
######1   
    PresentSpaceBar()
    trial1 = TextStimulus(txt = "In a given trial, you will see grids that look like this:", p = [0, 370])
    DrawGrid(opcty=1, ca = inst_ca_pos, ts=inst_temp_sqr)
    trial2 = TextStimulus(txt = "The computer will randomly select one square out of the grid.\n\n Your task is to predict the color of the square that the computer will select as accurately and promptly as possible.", p = [0, -200])
    win.flip()
    event.waitKeys(keyList='space')
          
######2  
    PresentSpaceBar()
    keypage1 = TextStimulus(txt = "You can indicate your color prediction by pressing either ‘z’ or '/' key \n\n To indicate that you are predicting the color on the left corner, press 'z' key \n To indicate that you are predicting the color on the right corner, press '/' key", p = [0, 300])
    DrawGrid(opcty=1, ca = inst_ca_pos,ts=SetGridParameters(scale = 1/2, y =-50)[0])
    DrawRespKey()[0].draw()
    DrawRespKey()[1].draw()
    win.flip()
    event.waitKeys(keyList='space')
     
#######3    
    PresentSpaceBar()
    pointSystem = TextStimulus(txt = "Throughout the trials, the colors of the squares may vary. \n\nThe colors of the randomly selected square worth point amounts as illustrated below.", p = [0, 170])
    posText = TextStimulus(txt = "+10 \n points", h = 30, p = [-200, -80],b =True)
    neutText = TextStimulus(txt = "0 \n points", h = 30, p = [0, -80],b =True)
    pnegText = TextStimulus(txt = "-10 \n points", h = 30, p = [200, -80],b =True)
    posSquare= DrawSquares(sqrsz= 80, xpos=-200, ypos=0, col='darkred')
    neutSquare= DrawSquares(sqrsz= 80, xpos=0, ypos=0, col='darkgrey')
    negSquare= DrawSquares(sqrsz= 80, xpos=200, ypos=0, col='darkblue')
    posSquare.draw()
    neutSquare.draw()
    negSquare.draw()
    win.flip()
    event.waitKeys(keyList='space')

#######4 
    PresentSpaceBar()
    exmaple1 = TextStimulus(txt = "For instance, imagine you are presented with the following gird. \n\n  You will receive:\n\n +10 points if the computer randomly selects a red square \n 0 points if the computer randomly selects a grey square \n\n", p = [0, 370], v = "top")
    DrawGrid(opcty=1, ca = inst_ca_pos, ts=SetGridParameters(scale = 3/7, y =-100)[0])
    win.flip()
    event.waitKeys(keyList='space')
    
#######5  
    PresentSpaceBar()
    exmaple2 = TextStimulus(txt = "For instance, imagine you are presented with the following gird. \n\n  You will receive:\n\n -10 points if the computer randomly selects a blue square \n 0 points if the computer randomly selects a grey square \n\n", p = [0, 370], v = "top")
    DrawGrid(opcty=1, ca = inst_ca_neg, ts=SetGridParameters(scale = 3/7, y =-100)[0])
    win.flip()
    event.waitKeys(keyList='space')

#######6  
    PresentSpaceBar()
    accuracyInst = TextStimulus(txt = "Also, being as accurate in your predictions is very important \n\n Note that accuracy is calculated SPEREATELY from the points you receive.", p = [0, 250], v = "top")
    win.flip()
    event.waitKeys(keyList='space')
    
#######7   
    PresentSpaceBar()
    lastInst = TextStimulus(txt = "Now the main trial will begin.\n\n Again, your goal is to predict as accurately and promptly as possible \n what the color of the randomly drawn square will be.")
    win.flip()
    event.waitKeys(keyList='space')
    

#######Run a trial (this function is equivalent to a single trial)
#Inputs
#   runInfo = array containing trial information parameters [outcome valence, critical square color, neutral square color, point, proportion]
def RunTrial(runInfo = ['pos','darkred', 'gray', 0, .5]):
    global total_point
    global accuracy
    global trial_prog
    global block_prog
    
######Save trial info
    
    outval = runInfo[0] #outcome valence
    crit_col = runInfo[1] #color of the critical square
    neut_col = runInfo[2] #color of the neutral square
    point = runInfo[3] 
    prob = runInfo[4] #proportion of critical square in the grid
    
    #save trial info
    trialInfo = ",blockNo," + str(block_prog) + ",trialNo," + str(trial_prog) + ",OutcomValence," + outval + ",critColor," + crit_col + ",point," + str(point) + ",prob," + str(prob)


#######Draw a grid stimuli until key input/time limit
        
    #reset boolean and input every start of the trial
    continuing = True
    kb.clock.reset()
    kb.clearEvents()
    
    
    #Set grid pattern within the trial
    colArray = SetGridPattern(crit_col = runInfo[1], neut_col = runInfo[2], prob = runInfo[4])
    
    #calculate when to stop
    trial_stop = core.getTime() + trial_dur
    
    while continuing and core.getTime() < trial_stop: 
        ptbKeys = kb.getKeys(respKeys, waitRelease=False)
        
        #present grid stimuli
        DrawGrid(ca= colArray)
        
        #draw corresponding color squares for response keys each corner
        DrawRespKey(cc = runInfo[1], nc = runInfo[2])[0].draw()
        DrawRespKey(cc = runInfo[1], nc = runInfo[2])[1].draw()
        
        #check for key input and save resp info
        if ptbKeys != [] and ptbKeys[0].name  != 'space':
            if ptbKeys[0].name == 'z':
                keyResp = "left"
            elif ptbKeys[0].name  == 'slash':
                keyResp = "right"
            elif ptbKeys[0].name  == 'escape':
                win.close()
                core.quit()
           
            keyRT = f"{ptbKeys[0].rt:.4f}"
            continuing = False
            
        win.flip()
    
    #if keys were not pressed, save null response info as resp_entry
    if ptbKeys ==[]:
        keyResp = "NaN"
        keyRT = "-999"
    
    #save response entry
    resp_entry = ",keyResp," + keyResp + ",keyRT," + keyRT
    

#######Present feedback: Retract the grid except for the one randomly chosen square, and show how much point has been endowed/lost
    #present the identical grid as previously presented but in lower opacity
    DrawGrid(opcty = .2, ca= colArray)
    
    #Get random square from the temp_sqr and present it with full opacity
    randsqr_x = randrange(grid_N)
    randsqr_y = randrange(grid_N)
    temp_sqr[randsqr_x][randsqr_y].opacity =1
    temp_sqr[randsqr_x][randsqr_y].draw()

    win.flip()
    core.wait(sqr_fb_dur)

    #Retrieve and present information about the randomly chosen sqaure
    randsqr_color = colArray[randsqr_x*grid_N+randsqr_y] #the color of randomly chosen square
    if randsqr_color == crit_col: #if the color of randomly chosen square was a critical square
        total_point += point #calculate total point so far by adding the trail point amount
        if ptbKeys != []:
            if ptbKeys[0].name == 'z': #if participant predicted correctly add 1 for accuracy
                accuracy += 1
    elif randsqr_color == neut_col: #if the color of randomly chosen square was a neutral square no points are given
        if ptbKeys != []:
            if ptbKeys[0].name == 'slash': #if participant predicted correctly add 1 for accuracy
                accuracy += 1
    
    #calculate current accuracy level    
    acc_score = round(accuracy/trial_prog*100,2) 
    
    #present how much points has been awarded
    PointText = visual.TextStim(win, text = "Current Point Total : {}".format(total_point), pos=[0,-200], color='white', units='pix', height=40, wrapWidth = 1000)
    temp_sqr[randsqr_x][randsqr_y].draw()
    PointText.draw()
    
    #save outcome info
    outcomes = ",outcomeColor," + randsqr_color + ",totalPoints," + str(total_point) + ",acc," + str(accuracy) + ",totalAcc," + str(acc_score)
    
    win.flip()
    core.wait(1)



#########Draw fixation cross
    fixation = visual.TextStim(win, text = "+", pos=[0,0], color='white', units='pix', height=50, )
    fixation.draw()
    win.flip()
    core.wait(fix_dur)
    

#########At the end of the block, show accuarcy feedback
    #if this is last trial of the block present following messages
    if trial_prog % block_done == 0:
        BlockText = visual.TextStim(win, text = "This is the end of the block {}.".format(int(trial_prog / block_done)), pos=[0,100], color='white', units='pix', height=40, wrapWidth = 1000)
        AccText = visual.TextStim(win, text = "Accuracy Level : {}%".format(acc_score), pos=[0,0], color='white', units='pix', height=40, wrapWidth = 1000)
        RestText = visual.TextStim(win, text = "You may take a short rest.\n When you are ready to resume please press the SPACEBAR", pos=[0,-150], color='white', units='pix', height=40, wrapWidth = 1600)
        
        BlockText.draw()
        AccText.draw()
        RestText.draw()
        win.flip()
        
        block_prog += 1
        
        event.waitKeys(keyList = 'space')
        win.flip()
    
    #save experiment/trial information and switch to the next row
    log_file.write(expInfo + trialInfo + resp_entry + outcomes + "\n")
    trial_prog += 1
    

def RunTask():
    global trial_seq
    
    for i in range(len(trial_seq)): #for number of trials set in trial_seq
        RunTrial(trial_seq[i][-5:]) #excecute RunTrial function with the last 4 parameters in trial_seq as input
    
    
def ShowDebrief():
    debrief_text = "Thank you for your participation. The study you just completed investigated how desires for a particular outcome might influence expectations about such outcomes and how that might vary based on the type of prediction you are making.\n\n In this study, you either won or lost points depending on the color from a random draw. If a possible color outcome was associated with earning points, we assumed you would want that outcome to occur in the hopes that higher points would terminate the task earlier. In actuality, the point system in this study was designed to ensure that you would go through at least 200 trials. \n\n Our interest was in whether this desire for the outcome would make you more optimistic than usual about that particular outcome. In other words, would your predictions be biased? Alternatively, perhaps wanting a particular outcome would make you pessimistic about it, because you wanted to avoid being disappointed by a negative outcome. We hypothesize that there will be an impact of desire such that people will be more likely to predict “winning” color even under conditions where this doesn’t seem to be the most likely outcome. Your data will be combined with others to help us address our questions. \n\n It is very important that you do not discuss this study with other students until after the semester. Discussing it before then could seriously jeopardize the results and would render the responses like yours of no use. We thank you for your cooperation. \n\n If you have any further questions about this study, please contact Prof. Paul Windschitl at 319-335-2435, or e-mail: paul-windschitl@uiowa.edu."
    Debrief = TextStimulus(txt = debrief_text, h = 25, p = [0, 40],a = "left")
    
    PresentSpaceBar()
    win.flip()
    event.waitKeys(keyList='space')
    

def TermainateTask():
    global win
    global log_file
       
    #close log file and window
    log_file.close()
    win.close()
    core.quit()


Instruction1()
RunTask()
ShowDebrief()
TermainateTask()













