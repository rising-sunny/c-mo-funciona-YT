# Voice used for the narrated prototype

Source: https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-en_US-ljspeech-high.tar.bz2

Engine: sherpa-onnx 1.13.8 (local CPU synthesis).
Voice: US English, female, synthetic. No voice cloning.

The supplied model card identifies the LJSpeech dataset as public domain.
The model card is reproduced below; this is provenance, not a separate license grant.

---

# Model card for ljspeech (high)

* Language: en_US (English, United States)
* Speakers: 1
* Quality: medium
* Samplerate: 22,050Hz

## Dataset

* URL: https://keithito.com/LJ-Speech-Dataset/
* License: public domain

## Training

See: https://brycebeattie.com/files/tts/

US English female voice. Single speaker. Trained from scratch for 1000 epochs on medium quality settings using the LJ Speech dataset. I reencoded the recordings to a bit rate of 22500 Hz so it would match other voices released for Piper TTS.


## Revision 5 voice

The current voice prototype uses Kokoro en v0.19, speaker index 1 (af_bella),
with a more conversational script and per-phrase delivery speeds.
Source: https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/kokoro-en-v0_19.tar.bz2
The distribution includes Apache License 2.0; its copy is saved as KOKORO_LICENSE.txt.
The prior LJSpeech narration is preserved with revision 4.
