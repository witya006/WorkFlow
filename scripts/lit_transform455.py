"""Finite rational oracle for the pinned light-direction instruction order.

This models PC/RC rounding,not the old CRT's error callbacks or status flags.
"""
import math,struct
from fractions import Fraction as Q


def value(bits):return Q(struct.unpack('<f',struct.pack('<I',bits))[0])
def bits(value):return struct.unpack('<I',struct.pack('<f',float(value)))[0]
def power(n):return Q(2)**n


def exponent(x):
    e=x.numerator.bit_length()-x.denominator.bit_length()
    return e-1 if x<power(e) else e


def rounded(x,precision,rc):
    x=Q(x)
    if not x:return x
    sign=-1 if x<0 else 1;x=abs(x);step=power(exponent(x)-precision+1)
    scaled=x/step;n,remainder=divmod(scaled.numerator,scaled.denominator)
    if rc==0:increment=remainder*2>scaled.denominator or remainder*2==scaled.denominator and n%2
    else:increment=bool(remainder) and (rc==1 and sign<0 or rc==2 and sign>0)
    return sign*(n+increment)*step


def sqrt_nearest(x,precision):
    step=power(exponent(x)//2-precision+1);scaled=x/(step*step)
    n=math.isqrt(scaled.numerator//scaled.denominator)
    midpoint=Q((2*n+1)**2,4)
    if scaled>midpoint or scaled==midpoint and n%2:n+=1
    return n*step


def environment(cw):
    precision={0:24,2:53,3:64}[(cw>>8)&3];rc=(cw>>10)&3
    return lambda x:rounded(x,precision,rc),lambda x:rounded(x,24,rc),precision


def normal(vector,cw):
    r,s,p=environment(cw);x,y,z=vector
    square=s(r(r(r(x*x)+r(y*y))+r(z*z)))
    if not square:return None # 0/0 produces the x87 indefinite NaN.
    length=s(sqrt_nearest(square,p))
    return [s(r(x/length)) for x in vector]


def direction(matrix,vector,cw):
    r,s,_=environment(cw);m=matrix
    difference=lambda a,b,c,d:r(r(m[a]*m[b])-r(m[c]*m[d]))
    c0=difference(10,5,9,6);c1=difference(10,4,8,6);c2=difference(4,9,5,8)
    determinant=r(r(r(m[0]*c0)-r(c1*m[1]))+r(c2*m[2]))
    inv=s(r(1/determinant));negative=s(-inv)
    a=[s(r(c0*inv)),s(r(difference(10,1,2,9)*negative)),s(r(difference(1,6,5,2)*inv)),Q(0),
       s(r(c1*negative)),s(r(difference(10,0,2,8)*inv)),s(r(difference(0,6,4,2)*negative)),Q(0),
       s(r(c2*inv)),s(r(difference(0,9,1,8)*negative)),s(r(difference(5,0,4,1)*inv)),Q(0)]
    x,y,z=vector
    transformed=[s(r(r(r(a[4+i]*y)+r(a[i]*x))+r(a[8+i]*z))) for i in range(3)]
    return normal(transformed,cw)
