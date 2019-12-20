class request:
    def __init__(self, u1army, u1name, u1action, u1attributes, u2army, u2name, u2action, u2attributes):
        self.u1army = u1army
        self.u1tname = u1name
        self.u1action = u1action
        self.u1attributes = u1attributes
        self.u2army = u2army
        self.u2name = u2name
        self.u2action = u2action
        self.u2attributes = u2attributes

# note on action formatting: actions are to be represented as a tuple, the first element being a string
# representing the action being taken, and the rest of the elements being laid depending on the action
#   - for example, ("bsattack,

