import os
from math import pi
import numpy as np
import scipy.signal

MESSAGE_DIMS = (1000,400)


class Info:
    pass


def booth():
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


def mix(sound1,sound2,max_length=None):
    if not max_length:
        max_length = max(sound1.shape[0],sound2.shape[0])
    sound1 = np.vstack([sound1, np.zeros((max_length - sound1.shape[0],2))])
    sound2 = np.vstack([sound2, np.zeros((max_length - sound2.shape[0],2))])
    return sound1 + sound2

def silence(length_ms,sample_rate_Hz):
    n = round(sample_rate_Hz * length_ms/1000.0)
    return np.zeros((n,2))


def sound_envelope(length_ms,ramp_ms,sample_rate_Hz):
    total_len = int(round(sample_rate_Hz * length_ms/1000.0))
    ramp_len = int(round(sample_rate_Hz * ramp_ms/1000.0))
    ramp_t = np.array(range(ramp_len))

    # amplitude envelope
    return np.hstack([-0.5*np.cos((pi*ramp_t)/ramp_len)+0.5,
                      np.ones(total_len - 2*ramp_len),
                      0.5*np.cos((pi*ramp_t)/ramp_len)+0.5])


def attenuate(xs,attenuation_dB):
    rms = np.sqrt(np.mean(xs**2))
    return (10**(-attenuation_dB/20.) * (xs/rms))

def tone(freq_Hz,length_ms,attenuation_dB,ramp_ms,sample_rate_Hz,phase=0):
    t = np.array(range(int(round(sample_rate_Hz * length_ms/1000.0))))
    envelope = sound_envelope(length_ms,ramp_ms,sample_rate_Hz)

    # unnormalized tone
    xs = envelope * np.sin(2*pi*t / (sample_rate_Hz/freq_Hz) + phase)

    # normalized tone
    xs = attenuate(xs,attenuation_dB)

    return np.vstack([xs, xs]).T


def notch_noise(low_Hz,high_Hz,length_ms,ramp_ms,atten_dB,
                sample_rate_Hz,order=5):
    total_len = int(round(sample_rate_Hz * length_ms/1000.0))
    envelope = sound_envelope(length_ms,ramp_ms,sample_rate_Hz)

    nyq = 0.5*sample_rate_Hz
    low = low_Hz / nyq
    high = high_Hz / nyq
    b,a = scipy.signal.butter(order,[low, high],btype='band')

    notch = envelope * scipy.signal.lfilter(b,a,2*np.random.rand(total_len)-1)
    notch = attenuate(notch,atten_dB)

    return np.vstack([notch, notch]).T


def lowpass_noise(high_Hz,length_ms,ramp_ms,atten_dB,
                sample_rate_Hz,order=5):
    total_len = int(round(sample_rate_Hz * length_ms/1000.0))
    envelope = sound_envelope(length_ms,ramp_ms,sample_rate_Hz)

    nyq = 0.5*sample_rate_Hz
    high = high_Hz / nyq
    b,a = scipy.signal.butter(order,high,btype='lowpass')

    notch = envelope * scipy.signal.lfilter(b,a,2*np.random.rand(total_len)-1)
    notch = attenuate(notch,atten_dB)

    return np.vstack([notch, notch]).T


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

class RandomSeed():
    def __init__(self,seed):
        self.seed = seed
    def __enter__(self):
        self.state = np.random.get_state()
        np.random.seed(self.seed)
    def __exit__(self,type,value,traceback):
        np.random.set_state(self.state)
        
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
