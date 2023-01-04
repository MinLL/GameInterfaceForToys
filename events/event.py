import re

class Event:
    def __init__(self, name, regex, function, group, case_sensitive, params, origin, shortname):
        self.shortname = shortname
        self.origin = origin
        self.name = name
        if case_sensitive:
            self.regex = re.compile(regex, re.I)
        else:
            self.regex = re.compile(regex)
        self.function = function
        self.group = group
        self.params = params

        


