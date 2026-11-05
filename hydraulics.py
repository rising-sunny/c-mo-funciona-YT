"""Ideal, quasi-static, air-free hydraulic demonstration in SI units.
Neglects friction, leakage, compressibility and hydrostatic head differences.
"""
import math


def quantities(p):
    required=('input_area_m2','output_area_m2','input_force_n','input_stroke_m')
    if any(type(p[k]) not in (float,int) or not math.isfinite(p[k]) or p[k]<=0 for k in required):
        raise ValueError('Hydraulic parameters must be finite and positive')
    ratio=p['output_area_m2']/p['input_area_m2']
    pressure=p['input_force_n']/p['input_area_m2']
    output_force=pressure*p['output_area_m2']
    output_stroke=p['input_stroke_m']/ratio
    return {'area_ratio':ratio,'gauge_pressure_pa':pressure,'output_force_n':output_force,
            'output_stroke_m':output_stroke,'transferred_volume_m3':p['input_area_m2']*p['input_stroke_m'],
            'input_work_j':p['input_force_n']*p['input_stroke_m'],
            'output_work_j':output_force*output_stroke}


def state(t,p,start=4.0,end=21.0):
    q=quantities(p)
    u=max(0.0,min(1.0,(t-start)/(end-start)))
    progress=u*u*(3-2*u)
    x=p['input_stroke_m']*progress
    y=x/q['area_ratio']
    return {'input_displacement_m':x,'output_displacement_m':y,
            'transferred_volume_m3':p['input_area_m2']*x,'progress':progress}
