"""Illustrative 1-DOF self-interrupting bell with a variable-inductance coil.
Linear magnetic material, lumped spring/damping, ideal snap contact, prescribed
impact restitution. Open-contact energy is dissipated in an effective transient
resistance (unshown arc/parasitic path), not set to zero instantaneously.
"""
import math


def quantities(p):
 for k in ['voltage_v','resistance_ohm','inductance_h','magnetic_c_hm','initial_gap_m','mass_kg','spring_n_m','damping_ns_m','open_resistance_ohm','stroke_m','open_at_m','close_at_m']:
  if not math.isfinite(p[k]) or p[k]<=0:raise ValueError('Bell parameters must be finite and positive')
 if not 0<p['close_at_m']<p['open_at_m']<p['stroke_m']<p['initial_gap_m']:
  raise ValueError('Invalid contact, stroke or gap ordering')
 if not 0<=p['restitution']<1:raise ValueError('Impact restitution must be in [0,1)')
 return {'steady_current_a':p['voltage_v']/p['resistance_ohm'],
         'initial_inductance_h':p['inductance_h']+p['magnetic_c_hm']/p['initial_gap_m'],
         'max_spring_force_n':p['spring_n_m']*p['stroke_m']}


def simulate(p,duration=1.5,dt=.00002):
 quantities(p);x=v=i=0.0;closed=True;rows=[];events=[]
 for n in range(round(duration/dt)+1):
  t=n*dt;gap=p['initial_gap_m']-x
  inductance=p['inductance_h']+p['magnetic_c_hm']/gap
  derivative=p['magnetic_c_hm']/gap**2
  fm=.5*i*i*derivative;fs=p['spring_n_m']*x
  rows.append(dict(t=t,x=x,v=v,current=i,closed=closed,magnetic_force=fm,spring_force=fs))
  resistance=p['resistance_ohm'] if closed else p['resistance_ohm']+p['open_resistance_ohm']
  voltage=p['voltage_v'] if closed else 0
  i=max(0,i+dt*(voltage-resistance*i-i*derivative*v)/inductance)
  v+=dt*(fm-fs-p['damping_ns_m']*v)/p['mass_kg'];x+=dt*v
  if x>=p['stroke_m']:
   x=p['stroke_m']
   if v>0:events.append({'t':t+dt,'type':'strike','speed':v});v=-p['restitution']*v
  if x<=0:
   x=0;v=max(0,-.1*v)
  if closed and x>=p['open_at_m']:
   closed=False;events.append({'t':t+dt,'type':'open'})
  elif not closed and x<=p['close_at_m']:
   closed=True;events.append({'t':t+dt,'type':'close'})
 return rows,events


def sample(rows,t):
 dt=rows[1]['t']-rows[0]['t'];index=max(0,min(len(rows)-2,int(t/dt+1e-9)))
 a,b=rows[index:index+2];u=max(0,min(1,(t-a['t'])/dt))
 result={k:a[k]+(b[k]-a[k])*u for k in ['x','v','current','magnetic_force','spring_force']}
 result['closed']=a['closed'];result['physical_time']=t
 return result


def prepare(config):
 rows,events=simulate(config['physics'])
 closes=[e['t'] for e in events if e['type']=='close']
 opened=next(e['t'] for e in events if e['type']=='open' and e['t']>closes[0])
 hit=next(e['t'] for e in events if e['type']=='strike' and e['t']>opened)
 period=closes[1]-closes[0];start=closes[0];end=closes[1]
 bounds={'overview':(.020,.020+3*period),'button':(start,start+.002),
  'coil':(start+.002,opened-.001),'contact':(opened-.001,opened+.00035),
  'release':(opened+.00035,hit+.002),'spring':(hit+.002,end+.0006),
  'repeat':(end+.0006,end+.0006+3*period),
  'finish':(end+.0006+3*period,end+.0006+5*period)}
 return rows,events,bounds


def display_state(t,config,prepared):
 rows,events,bounds=prepared
 shot=next(sh for sh in config['shots'] if sh['start']<=t<sh['end'])
 lo,hi=bounds[shot['id']];u=(t-shot['start'])/(shot['end']-shot['start'])
 result=sample(rows,lo+(hi-lo)*u);result['shot']=shot['id']
 result['slowdown']=(shot['end']-shot['start'])/(hi-lo)
 return result
