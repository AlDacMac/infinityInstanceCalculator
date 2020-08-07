from diceMaths.coreMaths import *


# Returns the average hits and crits for p1 in a contested roll as a tuple
def ContestedRollHitAvg(p1burst, p1target, p2burst, p2target):
    p1bonus = max(0, p1target - 20)
    p1target = min(20, p1target)
    p2bonus = max(0, p2target - 20)
    p2target = min(20, p2target)
    singleDiceHitProb = 0
    singleDiceCritProb = 0.0
    for i in range(1, 21):
        valueRolled = i + p1bonus
        print("rolled {0}".format(valueRolled))
        if(valueRolled == p1target or valueRolled > 20):
            probNoContest = probNone(p2burst, 1 + p2bonus, 20)
            probCritFromRoll = (1.0 / 20) * probNoContest
            singleDiceCritProb += probCritFromRoll
            print("crit probability: {0}".format(probCritFromRoll))
        elif(valueRolled < p1target):
            windowWithMods = min(20, (p2target - valueRolled + 1 + p2bonus))
            probNoContest = probNone(p2burst, windowWithMods, 20)
            probHitFromRoll = (1.0 / 20) * probNoContest
            singleDiceHitProb += probHitFromRoll
            print(probHitFromRoll)
    return (p1burst * singleDiceHitProb, p1burst * singleDiceCritProb)


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
