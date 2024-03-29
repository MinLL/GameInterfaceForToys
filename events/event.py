import re

class Event:
    def __init__(self, name, regex, function, group, case_sensitive, params, origin, shortname, toy_class):
        self.shortname = shortname
        self.origin = origin
        self.name = name
        if regex is not None:
            if case_sensitive:
                self.regex = re.compile(regex, re.I)
            else:
                self.regex = re.compile(regex)
        else:
            self.regex = None
        self.function = function
        self.group = group
        self.params = params
        self.toy_class = toy_class

        


