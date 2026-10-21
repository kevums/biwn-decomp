"""Apply declared RAM-only fixture effects without resetting live device state."""
import numpy as np

def apply(device,before,after):
    assert len(before)==len(after)==0x200000
    registers=device.registers()
    changes=np.flatnonzero(np.frombuffer(before,dtype=np.uint8)!=np.frombuffer(after,dtype=np.uint8))
    for address in changes:
        at=int(address);device.direct(at,1,after[at])
    assert device.registers()==registers,'RAM-only fixture changed blitter registers'
    return len(changes)
