from settings import WARN_ON_STACK_DUMP_SOUND
import types
import asyncio

if WARN_ON_STACK_DUMP_SOUND: import winsound

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

class ReloadToyEventModalException(Exception):
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
    if WARN_ON_STACK_DUMP_SOUND : winsound.PlaySound('SystemQuestion',winsound.SND_ASYNC)



# Run a task and wait for the result.
async def run_task(foo, run_async=False, window=False):
    if isinstance(foo, list):
        ret = []
        for item in foo:
            ret += [await run_task(item, run_async)]
            if window:
                window.Refresh()
        return ret
    if isinstance(foo, types.CoroutineType):
        if run_async:
            asyncio.create_task(foo)
        else:
            return await foo
            if window:
                window.Refresh()
    else:
        # No need to do anything if the task was not async.
        return foo
