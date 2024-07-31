from pydantic import BaseModel
import hashlib
from binascii import hexlify
from enum import Enum

class BIP329Enum(Enum):
    TYPE_TX     =   "tx"
    TYPE_ADDR   =   "addr"
    TYPE_PUBKEY =   "pubkey"
    TYPE_INPUT  =   "input"
    TYPE_OUTPUT =   "output"
    TYPE_XPUB   =   "xpub"
    TYPE_WALLET =   "wallet"
    TYPE_NOTE   =   "note"
    TYPE_PROOF  =   "proof"


class nostrProfile(BaseModel):
    name:           str = "Not set"
    display_name:   str = "Not set"
    about:          str = "Not set"
    picture:        str = "Not set"
    nip05:          str = "Not set"
    banner:         str = "Not set"
    website:        str = "Not set"
    lud16:          str = "npub@openbalance.app"

class mintRequest(BaseModel):
    unit:       str = "sat"
    amount:     int = 0    


class SafeboxItem(BaseModel):
    name:           str|None=None
    type:           BIP329Enum|None=None
    description:    str|None=None
    value:          str|None=None
   

    
    def gethash(self):       
        
        return hexlify(hashlib.sha256((self.name+self.description).encode()).digest()).decode()
    
    def get_d_tag(self, pubkey: str):       
        
        return hexlify(hashlib.sha256((self.name+self.description+pubkey).encode()).digest()).decode()