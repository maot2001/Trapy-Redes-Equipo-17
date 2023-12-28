data = b'some bytes'
"""
print(len(data))

a=buffer.pop()
print(a)
print(buffer)
print(len(buffer))
print (buffer)
print(data[:10])
byte_list = list(data)
print(byte_list)
"""


class bytes_buffer():
    def __init__(self,data:bytes):
        
        self.buffer=[ data[i:i+1] for i in range(0,len(data))]
        
    def pop(self)->bytes:
        if self.buffer:
         return self.buffer.pop()
    
    def pop_count(self,count:int)->list:
        return [self.buffer.pop() for _ in range(min(len(self.buffer),count))]
    
    def get_count_bytes(self,count:int)->bytes:
        return b''.join(self.pop_count(count))
    
    
    def __len__(self):
        return len(self.buffer)



b=bytes_buffer(data)

print(b.get_count_bytes(20))
"""   
print(b.buffer)
print(b.pop())
print(len(b))
print(b.buffer)
print(b.pop_count(2))
print(b.buffer)
print(b.pop_count(20))
print(b.buffer)
"""



print(len(b'holo mundo NVINVAUIERNVJSENVUJFNVUINEARUIVNARUIV'))