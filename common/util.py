class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class FatalException(Exception):
    pass

class ReloadException(FatalException):
    pass

def info(s):
    print("[GameInterfaceForToys] [i] " +str(s))

def success(s):
    print( "[GameInterfaceForToys] [+] " + str(s))

def fail(s):
    print("[GameInterfaceForToys] [-] " + str(s))
    # beep()

def beep():
    print("\a")


