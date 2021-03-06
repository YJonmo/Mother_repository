'''
from multiprocessing import Process, Lock

def f(l, i):
    l.acquire()
    print 'hello world', i
    l.release()

if __name__ == '__main__':
    lock = Lock()

    for num in range(10):
        Process(target=f, args=(lock, num)).start()
        
'''

'''        
from multiprocessing import Pool

def f(x):
    return x*x

if __name__ == '__main__':
    pool = Pool(processes=4)              # start 4 worker processes
    result = pool.apply_async(f, [10])    # evaluate "f(10)" asynchronously
    print result.get(timeout=1)           # prints "100" unless your computer is *very* slow
    print pool.map(f, range(10))
'''


'''
data = np.loadtxt("Output2.txt")
import matplotlib.pyplot as plt
time_inde = data[0] - data[0][0]
plt.plot(time_inde,data[1])
'''

'''
File_name = "Opterode_RecordingAt" + str('%i' %time.time())+ ".hdf5"
f = h5py.File(File_name + str('%i' %time.time())+ ".hdf5", "w")
Wavelength = f.create_dataset('Spectrumeter/Wavelength', (len(Wavelength),), dtype='f')
Data_Spectrumeter.attrs['Serial_number'] = np.string_(spec.serial_number)

http://blog.tremily.us/posts/HDF5/      a very good tutorial

for index,key in enumerate(ks[:10]):
    print index, key
    data = np.array(f[key].values())
    plt.plot(data.ravel())

plt.show()
'''


'''
from multiprocessing import Process, Lock
from multiprocessing.sharedctypes import Value, Array
from ctypes import Structure, c_double

class Point(Structure):
    _fields_ = [('x', c_double), ('y', c_double)]

def modify(n, x, s, A):
    n.value **= 2
    x.value **= 2
    s.value = s.value.upper()
    for a in A:
        print a
        a.x **= 2
        a.y **= 2

if __name__ == '__main__':
    lock = Lock()

    n = Value('i', 7)
    x = Value(c_double, 1.0/3.0, lock=False)
    s = Array('c', 'hello world', lock=lock)
    A = Array(Point, [(1.875,-6.25), (-5.75,2.0), (2.375,9.5)], lock=lock)

    p = Process(target=modify, args=(n, x, s, A))
    p.start()
    p.join()

    print n.value
    print x.value
    print s.value
    print [(a.x, a.y) for a in A]
'''



from multiprocessing import Process, Value, Array
import numpy as np
import time

def f1(n,):
    for I in range(5):
        time.sleep(.1)
        print 'process 1 is running'
    arr[:] = np.ones(shape=(6,1), dtype=float)
    Process1_Done.value = True

def f2(n,):
    while Process1_Done.value == False:
        print 'process 2 is running'
        time.sleep(0.1) 
    else: 
        arr[:] = np.array(arr[:])*2
        Process2_Done.value = True
        

if __name__ == '__main__':

    arr = Array('f', np.zeros(shape=(6,1), dtype=float))
    Process1_Done = Value('i', False)
    Process2_Done = Value('i', False)    
    
    p1 = Process(target=f1, args=(1,)).start()
    p1 = Process(target=f2, args=(1,)).start()
    # p1.start()    
    # p1.join()
    for I in range(100):
        time.sleep(.1)
        if Process2_Done.value == True :
            print 'Now both processes are done'
            print arr[:]
            print I
            break
        else:
            print arr[:]