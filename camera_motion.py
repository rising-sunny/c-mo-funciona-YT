"""Deterministic camera paths: eased perspective push-ins and orbital parallax."""
import math


def camera_pose(shot, progress):
    u = max(0, min(1, progress))
    ease = u*u*(3-2*u)
    target = [a+ease*b for a,b in zip(shot['target'], shot.get('target_shift', [0,0,0]))]
    direction = [a-b for a,b in zip(shot['camera'], shot['target'])]
    azimuth = math.atan2(direction[1],direction[0])+math.radians(shot.get('orbit_deg',0))*ease
    elevation = math.atan2(direction[2],math.hypot(*direction[:2]))
    elevation += math.radians(shot.get('rise_deg',0))*ease
    span = shot['scale']*(1+(shot.get('end_scale',shot['scale'])/shot['scale']-1)*ease)
    # 50 mm lens, 36 mm vertical sensor: target-plane vertical span = distance*36/50.
    distance = span*50/36
    position = [target[0]+distance*math.cos(elevation)*math.cos(azimuth),
                target[1]+distance*math.cos(elevation)*math.sin(azimuth),
                target[2]+distance*math.sin(elevation)]
    return position, target, span
