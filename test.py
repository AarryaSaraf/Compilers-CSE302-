from lib.mcs import *

def tester():
    test = [{SSATemp('x', 0), SSATemp('y', 0)}, {SSATemp('x', 0), SSATemp('196', 1), SSATemp('y', 0)}, 
            {SSATemp('x', 0), SSATemp('196', 1), SSATemp('y', 0)}, {SSATemp('x', 0), SSATemp('y', 0)},
            {SSATemp('x', 0), SSATemp('y', 0)}, {SSATemp('x', 0), SSATemp('y', 0)}]
    ig = buildIG(test)
    print(ig)
    mc = mcs(ig)
    print(mc)
    
        
tester()