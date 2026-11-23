from machine import Pin
import time
    

#assign the pin
ir = Pin(5,Pin.IN)

#define count , Max , buffer
count = 0
MAX = 100
buffer = [0]*MAX

class IRException(Exception):
    def __init__(self,message):
        super().__init__(message)



class decodeReturn:
    def __init__(self,error=False,message=None,decoded=None,addr=None):
        self.message=message
        self.decoded=decoded
        self.addr=addr

#write the handler
def on_edge(pin:Pin):
    global count
    if count<MAX:
        buffer[count]=time.ticks_us()
        count+=1
    

#attach handler to the interupt
ir.irq(trigger=Pin.IRQ_FALLING|Pin.IRQ_RISING,handler=on_edge)


def _near(v,target,tol=0.3)->bool:
    return target * (1-tol) < v < target * (1+tol) 

def _start(start):
    return _near(start[0],9000) and _near(start[1],4500)

#decoder
def decode(buffer,n)->decodeReturn:
    if n == 4:
        return decodeReturn(message="repeat") 
    elif n<68:
        raise IRException("less then 67 edges")
    d_buf = [time.ticks_diff(buffer[i],buffer[i-1]) for i in range(1,n)]
    if not _start(d_buf[:2]):
        raise IRException("start bit didn't match")
    bits = 0
    for i in range(32):
        d = d_buf[3+2*i]
        if _near(d,1687):
            bits |= (1<<i)
        elif not _near(d,562):
            raise IRException("{i}th bit corrupted")
        
    addr,addr_inv = bits & 0xFF, (bits>>8) & 0xFF
    cmd,cmd_inv = (bits>>16) & 0xFF, (bits>>24) & 0xFF
    
    if cmd ^ cmd_inv != 0xFF: raise IRException("cmd inverse didn't match")
    if addr ^ addr_inv != 0xFF: raise IRException("addr inverse didn't match")
    
    return decodeReturn(decoded=cmd,addr=addr)
    


def main():
    global count
    print("press a button")
    #create a infinite loop
    while True:
        #check if the button signal has ended
        if count>0 and time.ticks_diff(time.ticks_us(),buffer[count-1])>20_000:
            #print the edges and the durations
            n=count
            try:
                decode_obj = decode(buffer, n)
                ir.irq(handler=None)
                try:
                    if decode_obj.decoded is not None:
                        yield decode_obj.decoded,decode_obj.addr
                    else:
                        print(decode_obj.message)
                finally:                
                    count=0
                    ir.irq(trigger=Pin.IRQ_FALLING|Pin.IRQ_RISING,handler=on_edge)      
            except IRException as e:
                print(f"error:{e}, message:{e.message}")
                count=0
                
        time.sleep_ms(5)
        
if __name__=="__main__":
    for cmd in main():
        print(f"command:{cmd}")
    
    