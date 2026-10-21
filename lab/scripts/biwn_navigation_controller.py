"""Read-only waypoint steering through ordinary emulated controller buttons."""
import hashlib,json,math
from pathlib import Path

class Navigation:
    def __init__(self,plan,output):
        self.plan_path=Path(plan);self.plan=json.loads(self.plan_path.read_text());self.output=Path(output);self.index=0;self.decisions=[];self.complete=False
        self.waypoints=self.plan['waypoints'];assert 1<=len(self.waypoints)<=8
        for point in self.waypoints:assert set(point)=={'X','Z'}and all(type(v)is int and 0<=v<65536 for v in point.values())
        self.tolerance=self.plan.get('position_tolerance',8);assert 1<=self.tolerance<=32
        self.heading_tolerance=self.plan.get('heading_tolerance',7);assert type(self.heading_tolerance)is int and 0<=self.heading_tolerance<=7
    def step(self,raw,frame):
        assert len(raw)>=112
        g=lambda a,w=4:int.from_bytes(raw[a:a+w],'big')
        x,z,mode,heading=g(4),g(10),g(20,2),g(110,1);buttons=[];desired=None;error=None
        if mode==self.plan.get('stop_scene_mode',2):self.complete=True
        if not self.complete:
            if frame<=self.plan.get('opening_A_frames',9):buttons=['A']
            else:
                while self.index<len(self.waypoints):
                    point=self.waypoints[self.index];dx=point['X']-x;dz=point['Z']-z
                    if abs(dx)<=self.tolerance and abs(dz)<=self.tolerance:self.index+=1
                    else:break
                if self.index<len(self.waypoints):
                    point=self.waypoints[self.index];dx=point['X']-x;dz=point['Z']-z
                    desired=round(-math.atan2(dx,dz)*128/math.pi)&255;error=((desired-heading+128)&255)-128
                    if abs(error)>self.heading_tolerance:buttons=['L'if error>0 else'R']
                    else:buttons=['U','C']if max(abs(dx),abs(dz))>96 else['U']
        self.decisions.append(dict(frame=frame,X=x,Z=z,scene_mode=mode,heading=heading,waypoint=self.index,desired_heading=desired,heading_error=error,buttons=buttons,scene_change_complete=self.complete))
        return buttons
    def finish(self):
        windows=[]
        for row in self.decisions:
            if not row['buttons']:continue
            if windows and windows[-1]['stop_frame']==row['frame']and windows[-1]['buttons']==row['buttons']:windows[-1]['stop_frame']+=1
            else:windows.append(dict(start_frame=row['frame'],stop_frame=row['frame']+1,buttons=row['buttons']))
        (self.output/'navigation-decisions.json').write_text(json.dumps(self.decisions,indent=2)+'\n');(self.output/'navigation-input.json').write_text(json.dumps(dict(windows=windows),indent=2)+'\n')
        result=dict(status='controller_plan_scene_mode_changed'if self.complete else'controller_plan_incomplete',plan=str(self.plan_path),plan_sha256=hashlib.sha256(self.plan_path.read_bytes()).hexdigest(),frames=len(self.decisions),last=self.decisions[-1]if self.decisions else None,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),scope='Reads player X/Z/heading/scene mode and selects only ordinary button inputs. No RAM writes, actor relocation, readiness/clock/geometry patches or execution-provider changes. This planning run is not original/C comparison proof; replay recorded input windows separately.')
        (self.output/'navigation-report.json').write_text(json.dumps(result,indent=2)+'\n');return result
