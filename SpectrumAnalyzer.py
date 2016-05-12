import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.lines as line
import threading
import wave
import Queue
from scipy import signal

class recorder():
    
    def __init__(self):
        self.CHUNK = 4096                          
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 48100
        self.RECORD_SECONDS = 0.1
        self.window = signal.hamming(self.CHUNK)
        self.fig = plt.figure()
        self.real_time_axis = plt.subplot(212,xlim =(0,self.CHUNK),ylim =(-10000,10000))           #creating a plot for real time
        self.real_time_axis.set_title("Real Time")
        self.real_time_line = line.Line2D([],[])
        self.real_time_data = np.arange(0,self.CHUNK,1)
        self.real_time_x_data = np.arange(0,self.CHUNK,1)
        plt.yticks(np.arange(-10000,10000,1000))
        self.fft_axis = plt.subplot(211,xlim =(0,self.CHUNK/2+1),ylim =(1,1000000))                 #creating a plot for fft
        self.fft_axis.set_title("FFT Time")
        self.fft_line = line.Line2D([],[])
        self.fft_data = np.arange(0,self.CHUNK/2+1,1)
        self.fft_x_data = np.arange(0,self.CHUNK/2+1,1)
        plt.xticks(np.arange(0,self.CHUNK/2+1, 100))
        plt.axis([0,500,1,1000000])
        
#Real time plotting on the graph       
    def plot_ini(self):
        self.real_time_axis.add_line(self.real_time_line)
        self.fft_axis.add_line(self.fft_line)
        return self.fft_line,self.real_time_line
    
    def plot_up(self,frame):
        self.real_time_line.set_xdata(self.real_time_x_data)
        self.real_time_line.set_ydata(self.real_time_data)
        self.fft_line.set_xdata(self.fft_x_data)
        self.fft_line.set_ydata(self.fft_data)
        return self.fft_line, self.real_time_line
    
    def anim(self):
        self.ani = animation.FuncAnimation(self.fig, self.plot_up, init_func = self.plot_ini,
                                           frames = 1, interval = 30, blit = False)
#Sound Recording and Microphone init
    def rec(self):
        self.p = pyaudio.PyAudio()
        self.q = Queue.Queue()

    def callBack(self,in_data, frame_count, time_info, status):
        self.q.put(in_data)
        self.audioRec.set()
        return(None,pyaudio.paContinue)

    def recStart(self):
        self.stream = self.p.open(format = self.FORMAT, channels = self.CHANNELS, rate = self.RATE,
                input = True, output = False, frames_per_buffer = self.CHUNK,
                stream_callback = self.callBack)
        self.stream.start_stream()
#Main processing
    def threaded_recording(self): 
        while self.stream.is_active():
            self.audioRec.wait(timeout=1000)
            if not self.q.empty():
                self.data = self.q.get()
                while not self.q.empty():
                    self.q.get()
                self.real_time_data = np.frombuffer(self.data,np.dtype('<i2'))
                self.real_time_data = self.real_time_data * self.window
                self.fft_temp_data = np.fft.fft(self.real_time_data,self.real_time_data.size)
                self.fft_data = np.abs(self.fft_temp_data)[0:self.fft_temp_data.size/2+1]
            self.audioRec.clear()
#Thread        
    def contStart(self):
        self.audioRec = threading.Event()
        self.t = threading.Thread(target = self.threaded_recording)
        self.t.daemon = True
        self.t.start()
        
    def contStop(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
#Showing the plot           
    def plotGraph(self):
        plt.show()


r = recorder()
r.rec()
r.recStart()
r.anim()
r.contStart()
r.plotGraph()
r.contStop()

            
        
        
