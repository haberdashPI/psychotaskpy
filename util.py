import os
from math import pi
import numpy as np

MESSAGE_DIMS = (1000,400)

class Info:
    pass

def booth():
    booth_indices = {'left': 1,'middle': 2, 'right': 3,'corner': 4}
    
    try:
        with open('C:\\booth_name.txt','r') as f:
            booth = f.readline()
            return booth
    except:
        return "none"

def left(xs):
    xs[:,1] = np.zeros(xs.shape[0])
    return xs

def right(xs):
    xs[:,0] = np.zeros(xs.shape[0])
    return xs

def silence(length_ms,sample_rate_Hz):
    n = round(sample_rate_Hz * length_ms/1000.0)
    return np.zeros((n,2))

def tone(freq_Hz,length_ms,attenuation_dB,ramp_ms,sample_rate_Hz,phase=0):
    t = np.array(range(int(round(sample_rate_Hz * length_ms/1000.0))))
    ramp_t = np.array(range(int(round(sample_rate_Hz * ramp_ms/1000.0))))

    #pdb.set_trace()
    # amplitude envelope
    envelope = \
      np.hstack([-0.5*np.cos((pi*ramp_t)/len(ramp_t))+0.5,
                np.ones(len(t) - 2*len(ramp_t)),
                0.5*np.cos((pi*ramp_t)/len(ramp_t))+0.5])

    # unnormalized tone
    xs = envelope * np.sin(2*pi*t / (sample_rate_Hz/freq_Hz) + phase)

    # normalized tone
    rms = np.sqrt(np.mean(xs**2))
    xs = (10**(-attenuation_dB/20.) * (xs/rms))

    return np.vstack([xs, xs]).T

def unique_file(filename_pattern):
    index = 0
    fname = filename_pattern % index
    while os.path.exists(fname):
        index = index + 1
        fname = filename_pattern % index
    return fname

def nth_file(i,filename_pattern,give_up_after=10,wrap_around=False):
    index = 0
    count = 0
    fname = filename_pattern % index

    while count < i and index < count+give_up_after:
        print index
        index = index + 1
        fname = filename_pattern % index
        if os.path.exists(fname):
            count = count + 1

    if os.path.exists(fname):
        return fname
    else:
        if wrap_around and i > 0:
            return nth_file(i % (count+1),filename_pattern,give_up_after)
        raise RuntimeError(("Could not find the Nth file (N=%d) with pattern: '" % (i+1) +
                           filename_pattern + "'"))

class LineWriter:
    def __init__(self,filename,info,info_order):
        self.info = info
        self.info_order = info_order
        self.filename = filename
        self.written = False

    def __call__(self,info,info_order):
        with open(self.filename,'a') as f:
            if not self.written:
                self.written = True
                names = self.info_order + info_order
                header = ",".join(names) + "\n"
                f.write(header)
                
                self.call_info_order = info_order

            assert set(info.keys()) == set(self.call_info_order)

            #pdb.set_trace()

            values = [self.info[x] for x in self.info_order] + \
              [info[x] for x in self.call_info_order]
            line = ",".join(map(str,values)) + "\n"
            f.write(line)
