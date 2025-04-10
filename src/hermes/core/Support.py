from dataclasses import dataclass

# Size of KBuckets essentially
K_VAL = 5
# System wide Concurrency Parameter
A_VAL = K_VAL

B_VAL = 3

BUCKET_REFRESH_INTERVAL = 1000000000000

@dataclass
class Triple:
    '''
    Triple Data Class represents fundamental reference to other nodes stored in K-Buckets
    '''
    ip_address : str 
    udp_port : int 
    node_id : bytes 

    def __repr__(self):
        return f"<{self.node_id}> : <{self.ip_address}> : <{self.udp_port}>"

    def __eq__(self, other):
        if not isinstance(other, Triple):
            return NotImplemented
        return self.ip_address == other.ip_address and self.udp_port == other.udp_port and self.node_id == other.node_id
