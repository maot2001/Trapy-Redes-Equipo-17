

class Flags:
    def __init__(self):
        
        self.ACK:bool = False
        self.SYN:bool = False
        self.FIN:bool = False
        self.RST:bool = False
        self.LAS:bool = False
        self.CWR:bool = False
        self.ECE:bool = False
        self.URG:bool = False
        
        
    def update(self)->dict:
        _dict={"ACK":False,"SYN":False,"FIN":False,"RST":False,"LAS":False,"CWR":False,"ECE":False,"URG":False}
        self._dict["ACK"]=self.ACK 
        self._dict["SYN"]=self.SYN
        self._dict["FIN"]=self.FIN 
        self._dict["RST"]=self.RST
        self._dict["LAS"]=self.LAS
        self._dict["CWR"]=self.CWR 
        self._dict["ECE"]=self.ECE 
        self._dict["URG"]= self.URG 
        return _dict
    
    def make_connection(self):
        """
        Establece la conexión inicializando el atributo SYN a True.

        Este método es parte del proceso de establecimiento de la conexión TCP,
        donde SYN es una abreviatura de "synchronize". Al establecer SYN en 1,
        se indica que se está intentando iniciar una conexión.

        No toma ningún argumento y no devuelve ningún valor.
        """
        self.SYN = True

    def hand_shake_ACK(self):
        """
        Establece la conexión inicializando el atributo ACK a True.

        Este método es parte del proceso de establecimiento de la conexión TCP,
        donde ACK es una abreviatura de "acknowledge". Al establecer ACK en 1,
        se indica que se está intentando iniciar una conexión.

        No toma ningún argumento y no devuelve ningún valor.
        """
        self.SYN=True
        self.ACK = True
    def close_connection(self):
        """
        Cierra la conexión inicializando el atributo FIN a True.

        Este método es parte del proceso de cierre de la conexión TCP,
        donde FIN es una abreviatura de "finish". Al establecer FIN en 1,
        se indica que se está intentando cerrar la conexión.

        No toma ningún argumento y no devuelve ningún valor.
        """
        self.FIN = True
        
    def recive_ACK(self):
        """
        Sets the ACK flag to True.
        """
        self.ACK = True
        
    def from_bytes_to_flags(self,flags_bytes):
        flags = [(128,"cwr"), (64,"ece"), (32,"urg"), (16,"ack"), (8,"las"), (4,"rst"), (2,"syn"), (1,"fin")]
    
        num = int.from_bytes(flags_bytes, "big") if isinstance(flags_bytes, bytes) else flags_bytes
        for bit, flag in flags:
            if num & bit:
                if flag == "syn":
                    self.SYN=True
                if flag == "ack":
                    self.ACK=True
                if flag == "fin":
                    self.FIN=True
                if flag == "rst":
                    self.RST=True
                if flag == "las":
                    self.LAS=True
                if flag == "cwr":
                    self.CWR=True
                if flag == "ece":
                    self.ECE=True
                if flag == "urg":
                    self.URG=True
            
    def parse_flags(self,dict_flags:dict):
        c=dict_flags.keys()
        on_flags=[]
        off_flags=[]
        for key in  dict_flags.keys():
            if(dict_flags[key]):
                on_flags.append(key)
            else:
                off_flags.append(key)
        return on_flags,off_flags
            
                    
       
    def to_bytes(self, temp:bool=False) -> bytes:
        
        on_flags,off_flags=self.parse_flags(self.update())
       
        flags_bytes = {"cwr":128, "ece":64, "urg":32, "ack":16, "las":8, "rst":4, "syn":2, "fin":1}
        if not temp:
            for flag in on_flags:
                self.flags[flag] = True
            for flag in off_flags:
                self.flags[flag] = False
        
        flag_num = 0
        for flag in self.flags:
            flag_num += flags_bytes[flag] if self.flags[flag] else 0
        
        if temp:
            for flag in off_flags:
                flag_num -= flags_bytes[flag] if self.flags[flag] else 0
            for flag in on_flags:
                flag_num += flags_bytes[flag] if not self.flags[flag] else 0
        
        return flag_num.to_bytes(1, "big")
