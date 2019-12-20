def probNone(n, targetWindow, totalWindow):
    if targetWindow >= totalWindow:
        return 0.0
    elif targetWindow <= 0:
        return 1.0
    else:
        failWindow = float(totalWindow - targetWindow)
        probSingleFail = failWindow / totalWindow
        probTotalFail = probSingleFail ** n
        return probTotalFail


def probOneUp(n, targetWindow, totalWindow):
    return 1 - probNone(n, targetWindow, totalWindow)


def avgSuccesses(n, targetWindow, totalWindow):
    return n * targetWindow / float(totalWindow)
