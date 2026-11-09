"""Selected455 quake/sway scalar oracle,explicit target float stores and uint wrap.

Transcendentals use host libm;this does not establish old CRT/x87 equivalence.
"""
import math,struct

def f(x):return struct.unpack('<f',struct.pack('<f',x))[0]
def decode(x):return struct.unpack('<f',struct.pack('<I',x))[0]
def noise(x):
    x=((x<<13)^x)&0xffffffff
    return f(1-((x*(x*x*15731+789221)+1376312589)&0x7fffffff)*2**-30)

class Quake:
    def __init__(self):
        self.phase=0;self.period=5;self.duration=self.remaining=self.density=0.;self.amp=[0.]*3;self.scale=1.;self.enabled=False
        self.sd=self.sp=self.sr=0.;self.prev=[0.]*3;self.next=[0.]*3;self.seed=1;self.heading=(1.,0.)
    def state(self):return [self.duration,self.remaining,self.density,*self.amp,self.scale,self.sd,self.sp,self.sr,*self.prev,*self.next]
    def rand(self):self.seed=(214013*self.seed+2531011)&0xffffffff;return (self.seed>>16)&0x7fff
    def start(self,density_duration,dt):
        self.duration,self.density=density_duration;self.remaining=self.duration;self.phase=0
        self.period=((math.trunc(42/f(dt*1000)+f(.999))&0xffffffff)+1)&0xffffffff
        if not self.period:self.period=1
    def sway(self,dt):
        if not self.enabled:return [0.]*3
        self.sr=f(self.sr-dt)
        if self.sr<0:
            self.prev=self.next[:]
            self.next=[f((self.rand()% (math.trunc(256*self.sd)&0xffffffff)-128*self.sd)/256) for _ in range(3)]
            self.sr=f((self.rand()%(math.trunc(128*self.sp)&0xffffffff)-64*self.sp)/256+self.sp)
        ratio=f((self.sp-self.sr)/self.sp);angle=f(ratio*f(math.pi));c=f(math.cos(angle));mix=f((2-(c+1))*.5)
        return [f(a*mix+b*(1-mix)) for a,b in zip(self.next,self.prev)]
    def vector(self,dt,toggle):
        out=self.sway(dt)
        if self.remaining<=0:return out
        if self.phase%self.period==0:
            x,z=self.heading
            if abs(x)<f(.01) and abs(z)<f(.01):x=0
            length=f(math.sqrt(f(z*z+x*x)));angle=f(math.acos(f(x/length)))
            alpha=f(1-(self.duration-self.remaining)/self.duration)
            self.amp=[f(f(f(math.cos(angle))*toggle)*alpha*self.density),f(self.density*f(noise(math.trunc(dt*1000+200))*alpha*self.scale)),f(f(f(math.sin(angle))*toggle)*alpha*self.density)]
        self.phase+=1;out=[f(a/self.period*self.phase+b) for a,b in zip(self.amp,out)]
        if self.phase>=self.period:self.phase=0
        self.remaining=max(0.,f(self.remaining-dt));return out
    def matrix(self,dt,values):
        result=values[:]
        if self.remaining>0:
            self.remaining=max(0.,f(self.remaining-dt));alpha=f(1-(self.duration-self.remaining)/self.duration)
            for i in range(3):result[12+i]=f(self.density*f(noise(math.trunc(dt*1000+i*200))*alpha)+result[12+i])
        return result
    def event(self,row):
        dt=decode(row['dt']);p=list(map(decode,row['input']));op=row['op'];out=[]
        if op=='start':self.start(p,dt)
        elif op=='heading':self.heading=tuple(p)
        elif op=='seed':self.seed=int(p[0])
        elif op=='sway':self.sd=p[0];self.sp=p[1] or f(.02);self.sr=0.;self.enabled=True
        elif op=='stop':self.enabled=False
        elif op=='vector':out=self.vector(dt,row['toggle'])
        elif op=='matrix':out=self.matrix(dt,p)
        elif op=='view':
            #CLevel B38494 slot27 ->8E7850;INS has a different publish order.
            self.heading=(p[10],p[8])
            delta=self.vector(dt,row['toggle']);out=p[:]
            for i in range(3):out[12+i]=f(out[12+i]+delta[i])
            self.heading=(out[10],out[8]);out=out*2
        elif op=='density':
            x,y,z=[f(p[i+3]-p[i]) for i in range(3)];length=f(math.sqrt(f(y*y+x*x+z*z)));distance=f(max(0.,length-200));out=[max(0.,f(1-distance/600))]
        else:raise ValueError('Unknown trace operation:'+op)
        return out
