# GnuRadio_SDRSharp_NOAA_Decoder
Can decode NOAA-satellite apt-data-images by parsing IQ-Wav files that were recorded by SDRSharp.

I might create a new repository later with automatic decoding. (and reference it here)
Theoretically the signal can be improved if the model was trained at same location (with similar signal interferences).
Additionaly no change of variables should be needed.

I should create something similar like my trained model on:
https://www.kaggle.com/crazyt/automatic-picture-transmission-decoding

But I would need to search the FM-signal in the band.
So AM-based model cannot be used, sadly.
I would need to create a similar IQ-wav-file first (so I'm 100% shure about the data of the original image).
This should be possible with gnu-radio.

Problem is that I might need 2 models.
One model that finds the frequency of the signal in the Baseband and one that actually decodes the FM-signal.
