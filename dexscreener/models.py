from pydantic import BaseModel, Field
from typing import Optional
import datetime as dt


class BaseToken(BaseModel):
    address: str
    name: str
    symbol: str


    def json(self, *args, **kwargs):
        return super().json(*args, **kwargs)

    def to_dict(self):
        return {
            "address": self.address,
            "name": self.name,
            "symbol": self.symbol
        }


class TransactionCount(BaseModel):
    buys: int
    sells: int

    def json(self, *args, **kwargs):
        return super().json(*args, **kwargs)


class PairTransactionCounts(BaseModel):
    m5: TransactionCount
    h1: TransactionCount
    h6: TransactionCount
    h24: TransactionCount

    def json(self, *args, **kwargs):
        return {
            "m5": self.m5.json(*args, **kwargs),
            "h1": self.h1.json(*args, **kwargs),
            "h6": self.h6.json(*args, **kwargs),
            "h24": self.h24.json(*args, **kwargs)
        }


class _TimePeriodsFloat(BaseModel):
    m5: Optional[float] = 0.0
    h1: Optional[float] = 0.0
    h6: Optional[float] = 0.0
    h24: Optional[float] = 0.0


class VolumeChangePeriods(_TimePeriodsFloat):
    def json(self, *args, **kwargs):
        return {
            "m5": self.m5,
            "h1": self.h1,
            "h6": self.h6,
            "h24": self.h24
        }


class PriceChangePeriods(_TimePeriodsFloat):
    ...

    def json(self, *args, **kwargs):
        return super().json(*args, **kwargs)


class Liquidity(BaseModel):
    usd: Optional[float] = None
    base: float
    quote: float

    def json(self, *args, **kwargs):
        return super().json(*args, **kwargs)

    def to_dict(self):
        return {
            "usd": self.usd,
            "base": self.base,
            "quote": self.quote
        }


class TokenPair(BaseModel):
    chain_id: str = Field(..., alias="chainId")
    dex_id: str = Field(..., alias="dexId")
    url: str = Field(...)
    pair_address: str = Field(..., alias="pairAddress")
    base_token: BaseToken = Field(..., alias="baseToken")
    quote_token: BaseToken = Field(..., alias="quoteToken")
    price_native: float = Field(..., alias="priceNative")
    price_usd: Optional[float] = Field(None, alias="priceUsd")
    transactions: dict = Field(..., alias="txns")
    volume: Optional[dict] = Field(..., alias="volume")
    price_change: Optional[dict] = Field(..., alias="priceChange")
    liquidity: Optional[dict] = None
    fdv: Optional[float] = 0.0
    pair_created_at: Optional[dt.datetime] = Field(None, alias="pairCreatedAt")
    
    def to_dict(self):
        return {
            "chainId": self.chain_id,
            "dexId": self.dex_id,
            "url": self.url,
            "pairAddress": self.pair_address,
            "baseToken": self.base_token.to_dict() if hasattr(self.base_token, 'to_dict') else self.base_token,
            "quoteToken": self.quote_token.to_dict() if hasattr(self.quote_token, 'to_dict') else self.quote_token,
            "priceNative": self.price_native,
            "priceUsd": self.price_usd,
            "txns": self.transactions,
            "volume": self.volume,
            "priceChange": self.price_change,
            "liquidity": self.liquidity.to_dict() if self.liquidity and hasattr(self.liquidity, 'to_dict') else self.liquidity,
            "fdv": self.fdv,
            "pairCreatedAt": self.pair_created_at,
        }


class TokenLink(BaseModel):
    type: Optional[str] = None
    label: Optional[str] = None
    url: Optional[str] = None


class TokenInfo(BaseModel):
    url: str
    chain_id: str = Field(..., alias="chainId")
    token_address: str = Field(..., alias="tokenAddress")
    amount: float = 0.0
    total_amount: float = Field(0.0, alias="totalAmount")
    icon: Optional[str] = None
    header: Optional[str] = None
    description: Optional[str] = None
    links: list[TokenLink] = []

    def json(self, *args, **kwargs):
        return super().json(*args, **kwargs)

    def to_dict(self):
        return {
            "url": self.url,
            "chainId": self.chain_id,
            "tokenAddress": self.token_address,
            "amount": self.amount,
            "totalAmount": self.total_amount,
            "icon": self.icon,
            "header": self.header,
            "description": self.description,
            "links": [link.dict() for link in self.links]
        }



class OrderInfo(BaseModel):
    type: str
    status: str
    payment_timestamp: int = Field(..., alias="paymentTimestamp")

    def json(self, *args, **kwargs):
        return self.to_dict()

    def to_dict(self):
        return {
            "type": self.type,
            "status": self.status,
            "paymentTimestamp": self.payment_timestamp
        }
