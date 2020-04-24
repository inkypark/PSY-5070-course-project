import random
import numpy

#Generates block sequences
#Inputs:
#   possible outcomes: array of integers, range of possible points amounts (i.e. outcomes) 
#   block repeat: an integer, defines how many times the block repeats

def GenerateBlockSeq(possible_outcomes = [10,-10], block_repeat = 2, pos_col = 'darkred' , neg_col= 'darkblue'):
    
    blocks = []
    outcome_levels = possible_outcomes
    outcome_col = [pos_col, neg_col, 'gray'] #array of possible colors depending on outcomes (i.e. positive,negative,neutral)
    
    
    for i in range(block_repeat):
        for j in range(len(outcome_levels)):
            if outcome_levels[j] > 0:
                outVal = 'pos' #if the possible outcomes are greater than 0, then the outcome valence is positive
                b = [outVal,outcome_col[j],outcome_col[-1],outcome_levels[j]]
            elif outcome_levels[j] < 0:
                outVal = 'neg' #if the possible outcomes are less than 0, then the outcome valence is negative
                b = [outVal,outcome_col[j],outcome_col[-1],outcome_levels[j]]
            blocks.append(b)
    
    return blocks 



#Generates randomized trial sequences and calculate trial number that will show block-level feedback
#Inputs:
#   blocksetup: array containing an array and a integer, sets up block parameters. See comment for GenerateBlockSeq function
#   prob start/end/space: set of floats, defines the lowest & highest probability presented in the task 
#   set repeat: an integer, defines how many times the set of trials repeats within a block
#outputs:
#   trials: array
#   block_done

def GenerateRandTrialSeq(blocksetup = [[10,-10],4], prob_start=.3, prob_end=.7, prob_space=.1, set_repeat=2):
        
    block_seq = GenerateBlockSeq(blocksetup[0],blocksetup[1])
    
    trials = []
    trials_sub = []
    prob_levels = numpy.arange(prob_start, prob_end + prob_space, prob_space) #calculate 
    
    block_counter = 1
    subblock_counter = 1

    for block in block_seq:
        for i in range(set_repeat):
            for prob in prob_levels:
                #current trial parameters
                t = [block_counter] +[subblock_counter] + block + [round(prob,2)]
                trials_sub.append(t)
                random.shuffle(trials_sub)
            trials += trials_sub
            trials_sub=[]
            subblock_counter += 1
        block_counter += 1
    
    #add trial number for the trial setup information
    for trialCount in range(len(trials)):
        trials[trialCount].insert(2, trialCount+1) 
        
    #calculate the number of trials included in the highest level of block -> will be used to identify the location where we show RPs block feedback (e.g. point when both neg, pos sublocks are done) 
    block_done = len(prob_levels) * set_repeat * len(blocksetup[0])
    
    return [trials, block_done]

