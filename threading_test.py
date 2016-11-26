import time
from threading import Thread
from multiprocessing import Process, Queue, Value, Pool, TimeoutError
import os

best = 0
stopping = False
sub = 0

def count(n):
    best=0
    while True:
        best+=1
        if (best % 100000 == 0):
            n.value  += best
            best = 0


def stop():
    global stopping
    stopping = True

def timed_count(limit):
    global sub
    num = Value('i', 0)
    t = Process(target = count, args = (num,))
    t2 = Process(target = count, args = (num,))
    t3 = Process(target = count, args = (num,))
    t4 = Process(target = count, args = (num,))
    t.start()
    t2.start()
    t3.start()
    t4.start()
    time.sleep(5)
    print(num.value)
    time.sleep(5)
    print(num.value)
#    t.join()
    t.terminate()
    t2.terminate()
    t3.terminate()
    t4.terminate()

def f(x):
    for i in range(10**7):
        x = x + i
    return x

def test_pool():    # start 4 worker processes
    with Pool(processes=4) as pool:

        # print "[0, 1, 4,..., 81]"
        print(pool.map(f, range(10)))

        # print same numbers in arbitrary order
        for i in pool.imap_unordered(f, range(10)):
            print("f=",i)

        num = Value("i",0)
        res = pool.apply_async(count, (num,))
        res.get(timeout=1)
        print("count = ", num.value)
        # evaluate "f(20)" asynchronously
        res = pool.apply_async(f, (20,))      # runs in *only* one process
        print("go")
        print(res.get(timeout=2))             # prints "400"

        # evaluate "os.getpid()" asynchronously
        res = pool.apply_async(os.getpid, ()) # runs in *only* one process
        print("pid=",res.get(timeout=1))             # prints the PID of that process

        # launching multiple evaluations asynchronously *may* use more processes
        multiple_results = [pool.apply_async(os.getpid, ()) for i in range(8)]
        print("pids=",[res.get(timeout=1) for res in multiple_results])

        # make a single worker sleep for 10 secs
        res = pool.apply_async(time.sleep, (10,))
        try:
            print(res.get(timeout=1))
        except TimeoutError:
            print("We lacked patience and got a multiprocessing.TimeoutError")

        print("For the moment, the pool remains available for more work")

    # exiting the 'with'-block has stopped the pool
    print("Now the pool is closed and no longer available")

if __name__=="__main__":
#        timed_count(1)
    test_pool()