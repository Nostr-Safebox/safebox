from pydantic import BaseModel
from datetime import datetime, timedelta
import jwt, re, requests, bech32
from time import sleep
import asyncio
from zoneinfo import ZoneInfo

from bech32 import bech32_decode, convertbits
import struct, json

from fastapi import FastAPI, HTTPException
from app.appmodels import RegisteredSafebox, CurrencyRate
from sqlmodel import Field, Session, SQLModel, create_engine, select
from app.config import Settings

settings = Settings()
engine = create_engine(settings.DATABASE)
# SQLModel.metadata.create_all(engine, checkfirst=True)

async def refresh_currency_rates():
    refresh_time = datetime.now()
    print("refresh currency rates:")
    currency_table = json.loads(requests.get('https://blockchain.info/ticker').text)
    
    with Session(engine) as session:
        statement = select(CurrencyRate).where(CurrencyRate.currency_code.in_(settings.SUPPORTED_CURRENCIES))
        results = session.exec(statement).all()
        for record in results:
            # print(f"{record.currency_code} {currency_table[record.currency_code]['15m']}")
            record.currency_rate = currency_table[record.currency_code]['15m']
            record.refresh_time = datetime.now()
        session.commit()

async def init_currency_rates():
   
    supported_currencies = []

    satoshi = CurrencyRate(currency_code="SAT", currency_rate=1e8)
    cad     = CurrencyRate(currency_code="CAD", currency_rate=1e8)
    usd     = CurrencyRate(currency_code="USD", currency_rate=1e8)
    gbp     = CurrencyRate(currency_code="GBP", currency_rate=1e8)
    eur     = CurrencyRate(currency_code="EUR", currency_rate=1e8)
    
    supported_currencies = [satoshi,cad,usd,gbp,eur]

    with Session(engine) as session:
        
        statement = select(CurrencyRate).where(CurrencyRate.currency_code=='SAT')
        result = session.exec(statement).first()
        if not result:
            session.add(satoshi)
            session.commit()




if __name__ == "__main__":
    refresh_currency_rates()