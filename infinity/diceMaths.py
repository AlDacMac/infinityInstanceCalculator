from diceMaths.coreMaths import *

# Returns the average hits and crits for p1 in a contested roll as a tuple
def ContestedRollHitAvg(p1Burst, p1Target, p1Bonus, p2Burst, p2Target, p2Bonus):
    singleDiceHitProb = 0
    singleDiceCritProb = 0.0
    for i in range(1, 21):
        valueRolled = i + p1Bonus
        print("rolled {0}".format(valueRolled))
        if(valueRolled == p1Target or valueRolled > 20):
            probNoContest = probNone(p2Burst, 1+p2Bonus, 20)
            probCritFromRoll = (1.0 / 20) * probNoContest
            singleDiceCritProb += probCritFromRoll
            print("crit probability: {0}".format(probCritFromRoll))
        elif(valueRolled < p1Target):
            windowWithMods = min(20, (p2Target - valueRolled + 1 + p2Bonus))
            probNoContest = probNone(p2Burst, windowWithMods, 20)
            probHitFromRoll = (1.0 / 20) * probNoContest
            singleDiceHitProb += probHitFromRoll
            print(probHitFromRoll)
    return (p1Burst * singleDiceHitProb, p1Burst * singleDiceCritProb)


def ContestedRollCritAvg(p1Burst, p1Target, p1Bonus, p2Burst, p2Target, p2Bonus):
    singleDiceProb = 0.0
    for i in range(1, 21):
        valueRolled = i + p1Bonus
        print("rolled {0}".format(valueRolled))
        if (valueRolled == p1Target or valueRolled > 20):
            probNoContest = probNone(p2Burst, 1 + p2Bonus, 20)
            probHitFromRoll = (1.0 / 20) * probNoContest
            singleDiceProb += probHitFromRoll
            print(probHitFromRoll)
    return p1Burst * singleDiceProb


            

