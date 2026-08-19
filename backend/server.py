from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import httpx
import os
import websockets
import json
from websockets.asyncio.client import connect
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("API_KEY")

app = FastAPI()

@app.get("/")
def root():
    return {"Hello": "World"}


# Pydantic Schema Models
class QuoteResponse(BaseModel):
    price: float
    change: float
    change_percent: float

class Stock(BaseModel):
    description: str
    displaySymbol: str
    symbol: str
    type: str

class SearchResponse(BaseModel):
    count: int
    result: list[Stock]


class SubscribeMsg(BaseModel):
    type: str = "subscribe"
    symbol: str

class TradeInfo(BaseModel):
    price: float = Field(alias="p")
    symbol: str = Field(alias="s")
    time: int = Field(alias="t")
    volume: float = Field(alias="v")

class Trade(BaseModel):
    data: list[TradeInfo]
    type: str


# Finnhub Endpoints
@app.get("/api/search/{stock}")
async def search_stock(stock: str):
    async with httpx.AsyncClient() as client:
        data = await client.get(f"https://finnhub.io/api/v1/search",
                                params={"q": stock, "exchange": "US", "token": api_key})
        response = data.json()
        return response
    
async def fetch_quote(symbol: str) -> QuoteResponse:
    async with httpx.AsyncClient() as client:
        data = await client.get(f"https://finnhub.io/api/v1/quote",
                                params={"symbol": symbol, "token": api_key})
        
        raw = data.json()

        return QuoteResponse(
            price=raw["c"],
            change=raw["d"],
            change_percent=raw["dp"]
        )

@app.get("/api/quote/{stock_symbol}")
async def quote_stock(stock_symbol: str):
    return await fetch_quote(stock_symbol)

@app.get("/api/stocks")
async def fetch_stock_list():
    async with httpx.AsyncClient() as client:
        data = await client.get(f"https://static2.finnhub.io/file/privatedatany2/exchange/USf.json?Authorization=3_20260805105447_fea32d1ac3e5923b6a8761db_f00f88452b983027fec7adde05ff9afb54112bb0_002_20260806105447_0017_dnld")
        # https://finnhub.io/api/v1/stock/symbol?exchange=US&mic=XNYS&token={api_key}
        response = data.json()
        return response

# Websocket Connection (Finnhub Trades)

# Server to Client (browser frontend)
@app.websocket("/ws/trades")
async def websocket_trades(websocket: WebSocket):
    # Server agrees to browser, handshake completes
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_json()
            print(data)
            
    except WebSocketDisconnect:
        pass


# Client to Server API (Finnhub)
async def finnhub_websocket(subscribe_msg: SubscribeMsg):

    async with connect(f"wss://ws.finnhub.io?token={api_key}") as ws:
        await ws.send(subscribe_msg.model_dump_json())

        try:
            async for raw in ws:
                data = json.loads(raw)
                print(data["type"])

        except websockets.exceptions.ConnectionClosed:
            print("Connection to API dropped")
