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

from find_noa_block import find_noa_block  # grc-generated hier_block
from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from optparse import OptionParser
import datetime
import numpy as np

IQ_FILE = r"d:\Program Files (x86)\SDRSharp\NOAA15\SDRSharp_20190112_173333Z_138063526Hz_IQ.wav"
samp_rate = 2048000
Center_Frequency = 137622000
Total_Center_Frequency = 138063526
Relative_Center_Frequency = Total_Center_Frequency-Center_Frequency

NOT_FOUND = True
FOUND_IN_ROW = 0
FIR_NEED = 10
LAST_XFREQ = 0
THRESHOLD = 2.6
THRESHOLD2 = 0.1
THRESHOLD3 = 0.01
GAP_WIDTH = 1000
pos = 0
print("Total_Center_Frequency: %f" % Total_Center_Frequency)
print("Relative_Center_Frequency: %f" % Relative_Center_Frequency)


def upd_samp_rate(sr):
    samp_rate = sr

class find_noa_freq_out(gr.basic_block):
    def __init__(self):
        global samp_rate ,NOT_FOUND, Relative_Center_Frequency
        gr.basic_block.__init__(
            self,
            name="OUT Find NOA frequency",
            in_sig = [(np.float32,samp_rate)],
            out_sig = None
        )
    
    def general_work(self, input_items, output_items):
        global samp_rate,THRESHOLD,THRESHOLD2,THRESHOLD3
        global GAP_WIDTH,NOT_FOUND,FOUND_IN_ROW
        global LAST_XFREQ,Relative_Center_Frequency
        global pos
        
        in0 = input_items[0]
        in00 = in0[0]
        l = len(in0)
        l00 = len(in00)
        lo = len(output_items)
        X = np.abs(np.fft.fft(in00))
        
        if NOT_FOUND:
            print(datetime.datetime.now())
            found = False
            for i in range(0,len(X)-7*GAP_WIDTH):
                pos += 1
                tcheck1 = (X[i]>X[i+GAP_WIDTH]*THRESHOLD) and (X[i+2*GAP_WIDTH]>X[i+3*GAP_WIDTH]*THRESHOLD) and (X[i+4*GAP_WIDTH]>X[i+5*GAP_WIDTH]*THRESHOLD) and (X[i+6*GAP_WIDTH]>X[i+7*GAP_WIDTH]*THRESHOLD)
                tcheck2 = (abs(X[i]-X[i+2*GAP_WIDTH])<X[i]*THRESHOLD2) and (abs(X[i+2*GAP_WIDTH]-X[i+4*GAP_WIDTH])<X[i+2*GAP_WIDTH]*THRESHOLD2) and (abs(X[i+4*GAP_WIDTH]-X[i+6*GAP_WIDTH])<X[i+4*GAP_WIDTH]*THRESHOLD2)
                if tcheck1 and tcheck2:
                    found = True
                    xfreq = i*(Total_Center_Frequency-Center_Frequency)/(samp_rate/2)-Relative_Center_Frequency
                    if FOUND_IN_ROW != 0:
                        if abs(LAST_XFREQ - xfreq)< (xfreq*THRESHOLD3):
                            FOUND_IN_ROW = 0
                    LAST_XFREQ = xfreq
                    FOUND_IN_ROW += 1
                    if FOUND_IN_ROW == FIR_NEED:
                        print("\nFound xfreq: %d at %f s, you can now stop." % (xfreq,pos/samp_rate))
                        NOT_FOUND = False
            if not found:
                FOUND_IN_ROW = 0
        
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
