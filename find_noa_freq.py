#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: FG Find NOA frequency
# Generated: Wed May  1 16:24:25 2019
##################################################

import os
import sys
sys.path.append(os.environ.get('GRC_HIER_PATH', os.path.expanduser('~/.grc_gnuradio')))

from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from thread import start_new_thread
from concurrent.futures import ProcessPoolExecutor,ALL_COMPLETED
from optparse import OptionParser
import datetime
import time
import concurrent
import numpy as np

IQ_FILE = r"d:\Program Files (x86)\SDRSharp\NOAA15\SDRSharp_20190112_173333Z_138063526Hz_IQ.wav"
samp_rate = 2048000
BW = samp_rate
Relative_Center_Frequency = BW/2

NOT_FOUND = True
FOUND_IN_ROW = 0
FIR_NEED = 6
LAST_XFREQ = 0
THRESHOLD = 1.5
THRESHOLD2 = 0.5
THRESHOLD3 = 0.1
GAP_WIDTH = 4800
SIG_WIDTH = 200
pos = 0.0


def upd_samp_rate(sr):
    global samp_rate
    samp_rate = sr
    BW = samp_rate


def max_sig(X,i,n,v):
    startIdx = i+(n*2+v)*GAP_WIDTH
    m = max(X[startIdx:startIdx+SIG_WIDTH])
    return m
    
def find_xfreq(in00,lpos):
    global samp_rate,THRESHOLD,THRESHOLD2,THRESHOLD3
    global GAP_WIDTH,NOT_FOUND,FOUND_IN_ROW
    global LAST_XFREQ
    global Relative_Center_Frequency,BW
    
    rpos = 0
    X = np.abs(np.fft.fft(in00))
    if(os.path.isfile("snapshot.txt")):
        return True
    print("%s: %06.2f s [%09d] | len(X):%d" % (datetime.datetime.now(),lpos/samp_rate,lpos,len(X)))
    found = False
    for i in range(0,len(X)-14*GAP_WIDTH):
        rpos += 1
        tcheck1 = True
        for n in range(0,4):
            tcheck1 = tcheck1 and (max_sig(X,i,n,0)>max_sig(X,i,n,1)*THRESHOLD)
        for n in range(0,4):
            tcheck1 = tcheck1 and (max_sig(X,i,n,1)*THRESHOLD<max_sig(X,i,n,2))
        if tcheck1:
            found = True
            xfreq = i*BW/samp_rate-Relative_Center_Frequency
            if FOUND_IN_ROW != 0:
                if abs(LAST_XFREQ - xfreq)< (xfreq*THRESHOLD3):
                    FOUND_IN_ROW = 0
            LAST_XFREQ = xfreq
            FOUND_IN_ROW += 1
            if FOUND_IN_ROW == FIR_NEED:
                if(os.path.isfile("snapshot.txt")):
                    return True
                print("\nFound xfreq: %d at %06.2f s [%09d | i:%d], you can now stop." % (xfreq,lpos/samp_rate,lpos+rpos,i))
                for n in range(-16,16):
                    print("%d: %f,%f" % (n,max_sig(X,i,n,0),max_sig(X,i,n,1)))
                f = open("snapshot.txt","w+")
                d = 0
                for x in X:
                    f.write("%d,%f\n" % (d,x))
                    d += 1
                f.close()
                NOT_FOUND = False
                break
        else:
            FOUND_IN_ROW = 0
    print("%s ." % datetime.datetime.now())
    if not found:
        FOUND_IN_ROW = 0
    return not NOT_FOUND
        
class find_noa_freq_out(gr.basic_block):
    executor = ProcessPoolExecutor(max_workers=6)
    all_futures = []
    def __init__(self):
        global samp_rate ,NOT_FOUND, Relative_Center_Frequency
        gr.basic_block.__init__(
            self,
            name="OUT Find NOA frequency",
            in_sig = [(np.float32,samp_rate)],
            out_sig = None
        )
        try:
            os.remove("snapshot.txt")
        except:
            pass
    


        
    def general_work(self, input_items, output_items):
        global samp_rate,THRESHOLD,THRESHOLD2,THRESHOLD3
        global GAP_WIDTH,NOT_FOUND,FOUND_IN_ROW
        global LAST_XFREQ
        global Relative_Center_Frequency,BW
        global pos
        
        in0 = input_items[0]
        in00 = in0[0]
        l = len(in0)
        l00 = len(in00)
        lo = len(output_items)
        
        if NOT_FOUND:
            ndcnt = 0
            for f in self.all_futures:
                if not f.done():
                    ndcnt += 1
                elif f.result():
                    NOT_FOUND = False
                    self.consume(0, l)
                    self.produce(0, lo)
                    return 0
            if(os.path.isfile("snapshot.txt")):
                self.consume(0, l)
                self.produce(0, lo)
                return 0
            if ndcnt>=8:
                concurrent.futures.wait(self.all_futures,return_when=ALL_COMPLETED)
            a = self.executor.submit(find_xfreq,in00,pos)
            self.all_futures.append(a)
            pos += samp_rate
            if a is None:
                raise Exception("FAIL")
        
        self.consume(0, l)
        self.produce(0, lo)
        return 0

class find_noa_freq(gr.top_block):

    def __init__(self):
        global samp_rate,IQ_FILE
        gr.top_block.__init__(self, "TOP Find NOA frequency")

        ##################################################
        # Blocks
        ##################################################
        
        self.blocks_wavfile_source_0_0 = blocks.wavfile_source(IQ_FILE, False)
        upd_samp_rate(self.blocks_wavfile_source_0_0.sample_rate())
        self.blocks_stream_to_vector = blocks.stream_to_vector(gr.sizeof_float,samp_rate)

        self.out = find_noa_freq_out()

        self.connect((self.blocks_wavfile_source_0_0, 0), (self.blocks_stream_to_vector, 0))

        self.connect((self.blocks_stream_to_vector, 0), (self.out, 0))
        
        print("sample_rate: %d" % samp_rate)


def main(top_block_cls=find_noa_freq, options=None):
    tb = top_block_cls()
    tb.start()
    try:
        raw_input('Press Enter to quit: \n')
    except EOFError:
        pass
    tb.stop()
    tb.wait()


if __name__ == '__main__':
    main()
