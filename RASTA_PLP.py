import soundfile as sf
import numpy as np

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
%matplotlib inline

import gammatone.filters as gt_filters
import scipy.signal as dsp

def Hz2Bark(f):
    return 600*np.sinh(f/6.0)
def Bark2Hz(bark):
    return np.arcsinh(bark/600.0)*6.0

def FreqFilterMatrix(fs,fft_len,N,min_freq,max_freq,filter_type='bark'):
    # caculate the center frequency of 
    freq_resolution = np.float32(fs)/fft_len
    
    if filter_type == 'bark':
        step = (Hz2Bark(max_freq)-Hz2Bark(min_freq))/(N+1.0)
        cf =  step*np.arange(N+2)+min_freq
    else:
        raise Exception('error')
        
    cf_bin = np.int16(np.round(cf/freq_resolution))
    
    half_len = np.int16(np.floor(fft_len/2.0))
    
    f = freq_resolution*np.arange(half_len)
    matrix = np.repeat(f,axis=1,repeats=N)
    amp = np.zeros(half_len)
    for n in xrange(N):
        center_bin = cf_bin[n+1]
        
        low_width = cf[n+1]-cf[n]
        amp[:center_bin] = 1-(cf[n+1]-f[:center_bin])/low_width
        
        high_width = cf[n+2]-cf[n+1]
        amp[center_bin:] = 1-(f[center_bin:]-cf[n+1])/high_width
        
        amp[amp<0] = 0
        matrix[:,n] = amp

    return [matrix,cf]
    

def GetEqualLoudnes(f):
    fsq = bandcfhz**2;
    ftmp = fsq + 1.6e5;
    eql = np.multiply(((np.divide(fsq,ftmp))**2),np.divide(fsq+1.44e6,fsq + 9.61e6))
    return eql


def GetRASTA(wav_path):
    
    wav,fs = sf.read(wav_path)
    N = 26
    '''STFT'''
    frame_len = np.int16(25e-3*fs)
    overlap = np.int16(frame_len/2)
    f,t,spectrum = dsp.stft(x=wav,fs=fs,nperseg=frame_len,noverlap=overlap,window='hanning',padded=True)
    # spectrum = [bins,frame_time]
    
    # add constant to psd to avoid zeros
    psd = (np.abs(spectrum))**2 + frame_len
    
    # filter psd in frequency domain
    convert_matrix,cf = FreqFilterMatrix(fs=fs,fft_len=frame_len,N=N,min_freq=0,max_freq=fs/2,filter_type='bark')
    
    # convert_matrix = [bins,channels]
    psd_cb = np.dot(convert_matrix.T,psd)
    
    # compressing statistic nonlinear transformation
    psd_log = np.log(psd)
    
    ''' IIR filter '''
    # advance the psd_log by 4 samples
    psd_log[:-4] = psd_log[4:]; psd_log[-4:] = 0
    
    b = np.asarray([0.2,0.1,0,-0.1,-0.2])
    a = np.asarray([1,-0.94])
    psd_log_filtered = np.zeros_like(psd_log)
    psd_log_filtered = dsp.lfilter(a=a,b=b,x=psd_log[4:],axis=1)
    
    # expandin static nonlinear transformation
    psd_filted = 10**psd_log_filtered
    
    ''' Perceptual linear prediction'''
    # Multiply by equal loudness curve
    eql = GetEqualLoudnes(f=cf)
    eql = np.reshape(eql,newshape=[N,1])
    psd_eql = np.multiply(psd_filted.T,eql.T).T
    
    # power low (intensity to loudness)
    psd_loudness = psd_eql**0.33
    
    
    
    return psd_filted