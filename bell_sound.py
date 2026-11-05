"""Procedural inharmonic gong resonances at the displayed (slowed) impacts."""
import argparse
import json
from pathlib import Path
import numpy as np
import soundfile as sf


def generate(config,out):
 c=json.loads(config.read_text());events=json.loads((out/'bell-overlay-info.json').read_text())['displayed_impacts']
 rate=48000;mix=np.zeros(round(c['duration']*rate),dtype=np.float32);rng=np.random.default_rng(19)
 for event in events:
  t=np.arange(round(.9*rate))/rate
  sound=sum(amp*np.sin(2*np.pi*970*ratio*t)*np.exp(-t/decay) for ratio,amp,decay in [(1,.09,.32),(2.41,.045,.19),(3.73,.020,.12),(5.12,.008,.07)])
  sound+=rng.normal(0,.003,len(t))*np.exp(-t/.002)
  sound*=np.minimum(1,t/.0005)
  start=round(event['t']*rate);count=min(len(sound),len(mix)-start)
  if count>0:mix[start:start+count]+=sound[:count]
 sf.write(out/'bell-strikes.wav',mix,rate,subtype='PCM_24')
 (out/'bell-sound-info.json').write_text(json.dumps({'generator':'inharmonic modal synthesis','sample_rate':rate,'impacts':len(events),'peak':float(np.max(np.abs(mix)))},indent=2)+'\n')
 print('Synthesized',len(events),'illustrative gong strikes')


if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--episode',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();generate(a.episode,a.output)
