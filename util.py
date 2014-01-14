import os
from math import pi
import numpy as np

class Info:
    pass

def tone(freq_Hz,length_ms,attenuation_dB,ramp_ms,sample_rate_Hz):
    t = np.array(range(int(round(sample_rate_Hz * length_ms/1000.0))))
    ramp_t = np.array(range(int(round(sample_rate_Hz * ramp_ms/1000.0))))

    #pdb.set_trace()
    # amplitude envelope
    envelope = \
      np.hstack([-0.5*np.cos((pi*ramp_t)/len(ramp_t))+0.5,
                np.ones(len(t) - 2*len(ramp_t)),
                0.5*np.cos((pi*ramp_t)/len(ramp_t))+0.5])

    # unnormalized tone
    xs = envelope * np.sin(2*pi*t / (sample_rate_Hz/freq_Hz))

    # normalized tone
    rms = np.sqrt(np.mean(xs**2))
    xs = (10**(-attenuation_dB/20.) * (xs/rms))

    return np.vstack([xs, xs]).T

def rhythm_intervals(interval):
    if interval == 'A': return [107, 429, 214, 1065, 536, 643, 321, 857]
    else: raise Warning('No interval "'+interval+'" found.')

def unique_file(filename_pattern):
    index = 0
    fname = filename_pattern % index
    while os.path.exists(fname):
        index = index + 1
        fname = filename_pattern % index
    return fname

class LineWriter:
    def __init__(self,filename,info):
        self.info = info
        self.filename = filename
        self.written = False

    def __call__(self,info):
        with open(self.filename,'a') as f:
            if not self.written:
                self.written = True
                names = self.info.__dict__.keys() + info.__dict__.keys()
                header = ",".join(names) + "\n"
                f.write(header)
                
                self.init_order = self.info.__dict__.keys()
                self.call_order = info.__dict__.keys()

            assert list(info.__dict__.keys()) == list(self.call_order)

            #pdb.set_trace()

            values = [self.info.__dict__[x] for x in self.init_order] + \
              [info.__dict__[x] for x in self.call_order]
            line = ",".join(map(str,values)) + "\n"
            f.write(line)
