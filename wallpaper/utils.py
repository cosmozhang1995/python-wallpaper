def isiterable(o):
    try:
        list(o)
        return True
    except TypeError:
        return False

def setTimeout(callback, interval):
    import threading, time
    def thread_fn():
        time.sleep(interval)
        callback()
    thread = threading.Thread(target=thread_fn)
    thread.setDaemon(True)
    thread.start()
