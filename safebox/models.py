from pydantic import BaseModel
from typing import Union
import hashlib
from binascii import hexlify
from enum import Enum
from datetime import datetime

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

class DLEQ(BaseModel):
    """
    Discrete Log Equality (DLEQ) Proof
    """

    e: str
    s: str


class DLEQWallet(BaseModel):
    """
    Discrete Log Equality (DLEQ) Proof
    """

    e: str
    s: str
    r: str  # blinding_factor, unknown to mint but sent from wallet to wallet for DLEQ proof
    
class Proof(BaseModel):
    """
    Value token
    """

    # NOTE: None for backwards compatibility for old clients that do not include the keyset id < 0.3
    id: Union[None, str] = ""
    amount: int = 0
    secret: str = ""  # secret or message to be blinded and signed
    C: str = ""  # signature on secret, unblinded by wallet
    dleq: Union[DLEQWallet, None] = None  # DLEQ proof
    witness: Union[None, str] = ""  # witness for spending condition

    # whether this proof is reserved for sending, used for coin management in the wallet
    reserved: Union[None, bool] = False
    # unique ID of send attempt, used for grouping pending tokens in the wallet
    send_id: Union[None, str] = ""
    time_created: Union[None, datetime, str] = ""
    time_reserved: Union[None, datetime, str] = ""
    derivation_path: Union[None, str] = ""  # derivation path of the proof
    mint_id: Union[None, str] = (
        None  # holds the id of the mint operation that created this proof
    )
    melt_id: Union[None, str] = (
        None  # holds the id of the melt operation that destroyed this proof
    )

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

class mintQuote(BaseModel):
    quote:      str
    request:    str
    paid:       bool
    state:      str
    expiry:     int|None = None

class KeysetsResponseKeyset(BaseModel):
    id: str
    unit: str
    active: bool


class KeysetsResponse(BaseModel):
    keysets: list[KeysetsResponseKeyset]

class BlindedMessage(BaseModel):
    """
    Blinded message or blinded secret or "output" which is to be signed by the mint
    """

    amount: int
    id: str  # Keyset id
    B_: str  # Hex-encoded blinded message
    witness: Union[str, None] = None  # witnesses (used for P2PK with SIG_ALL)

class SafeboxItem(BaseModel):
    name:           str|None=None
    type:           BIP329Enum|None=None
    description:    str|None=None
    value:          str|None=None
   

    
    def gethash(self):       
        
        return hexlify(hashlib.sha256((self.name+self.description).encode()).digest()).decode()
    
    def get_d_tag(self, pubkey: str):       
        
        return hexlify(hashlib.sha256((self.name+self.description+pubkey).encode()).digest()).decode()