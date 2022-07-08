
import datetime
from time import mktime
from typing import Optional

from fastapi import FastAPI
from tinkoff.invest import Client
from tinkoff.invest import Share
from tinkoff.invest.services import InstrumentsService
from tinkoff.invest.schemas import OrderType
from tinkoff.invest.schemas import Quotation
from tinkoff.invest.schemas import InstrumentIdType
from tinkoff.invest.schemas import OrderDirection
from tinkoff.invest import GetAccountsResponse
from json import dumps, JSONEncoder
from fastapi.encoders import jsonable_encoder


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}

# GetAccounts
@app.get("/getaccounts/{token}")
async def read_item(token: str):
    print("GetAccounts")
    with Client(token) as client:
        print("\ntoken = ", token)

        try:
            rezult = client.users.get_accounts()
            print("\nrezult = ", rezult)
        except Exception as e:
            print("\nThere are no shares ", e)
            rezult = e

        json_rezult = jsonable_encoder(rezult)

        return json_rezult

# GetMarginAttributes
@app.get("/getmarginattributes/{token}")
async def read_item(token: str, account_id: str):
    print("GetMarginAttributes")
    with Client(token) as client:
        print("\ntoken = ", token)
        print("account_id = ", account_id)

        try:
            rezult = client.users.get_margin_attributes(account_id=account_id)
            print("\nrezult = ", rezult)
        except Exception as e:
            print("\nException ", e)
            rezult = e

        json_rezult = jsonable_encoder(rezult)

        return json_rezult

# GetInfo
@app.get("/getinfo/{token}")
async def read_item(token: str):
    print("GetInfo")
    with Client(token) as client:
        print("\ntoken = ", token)

        try:
            rezult = client.users.get_info()
            print("\nrezult = ", rezult)
            # rezult = {"prem_status": rezult.prem_status,
            #          "qual_status": rezult.qual_status,
            #          "qualified_for_work_with": rezult.qualified_for_work_with}
            # print("\nrezult = ", rezult)

        except Exception as e:
            print("\nException ", e)
            rezult = e

        json_rezult = jsonable_encoder(rezult)
        print("\njson_rezult = ", json_rezult)

        return json_rezult

# PostOrder
@app.get("/postsorder/{token}")
async def read_item(token: str, figi: str, quantity: int, price: Quotation, direction: OrderDirection,
                    account_id: str, order_type: OrderType, order_id: str):
    with Client(token) as client:
        print("\ntoken = ", token)
        print("figi = ", figi)
        print("quantity = ", quantity)
        print("price = ", price)
        print("direction = ", direction)
        print("account_id = ", account_id)
        print("order_type = ", order_type)
        print("order_id = ", order_id)

        try:
            rezult = client.orders.post_order(figi=figi, quantity=quantity, price=price, direction=direction,
                                              account_id=account_id, order_type=order_type, order_id=order_id)
            print("\nrezult = ", rezult)
        except Exception as e:
            print("\nException ", e)
            rezult = e

        json_rezult = jsonable_encoder(rezult)

        return json_rezult

# CancelOrder
@app.get("/cancelorder/{token}")
async def read_item(token: str, account_id: str, order_id: str):
    with Client(token) as client:
        print("\ntoken = ", token)
        print("account_id = ", account_id)
        print("order_id = ", order_id)

        try:
            rezult = client.orders.post_order(ccount_id=account_id, order_id=order_id)
            print("\nrezult = ", rezult)
        except Exception as e:
            print("\nException ", e)
            rezult = e

        json_rezult = jsonable_encoder(rezult)

        return json_rezult

# GetOrderState
@app.get("/getorderstate/{token}")
async def read_item(token: str, account_id: str, order_id: str):
    with Client(token) as client:
        print("\ntoken = ", token)
        print("account_id = ", account_id)
        print("order_id = ", order_id)

        try:
            rezult = client.orders.post_order(ccount_id=account_id, order_id=order_id)
            print("\nrezult = ", rezult)
        except Exception as e:
            print("\nException ", e)
            rezult = e

        json_rezult = jsonable_encoder(rezult)

        return json_rezult

@app.get("/shares/{token}")
async def read_item(token: str):
    with Client(token) as client:
        print("\ntoken = ", token)

        try:
            rezult = client.instruments.shares()
        except Exception as e:
            print("\nException ", e)
            rezult = e

        json_rezult = jsonable_encoder(rezult)

        return json_rezult


@app.get("/shareby/{token}")
async def read_item(token: str, figi: str):
    with Client(token) as client:
        print("\ntoken = ", token)
        print("\nfigi = ", figi)

        try:
            rezult = client.instruments.share_by(id_type=InstrumentIdType(1), id=figi)
        except Exception as e:
            print("\nException ", e)
            rezult = e

        json_rezult = jsonable_encoder(rezult)

        return json_rezult


# SandboxService


# GetSandboxAccounts
@app.get("/sandbox/getaccounts/{token}")
async def read_item(token: str):
    print("GetAccounts")
    with Client(token) as client:
        print("\ntoken = ", token)

        try:
            rezult = client.sandbox.get_sandbox_accounts()
            print("\nrezult = ", rezult)
        except Exception as e:
            print("\nThere are no shares ", e)
            rezult = e

        json_rezult = jsonable_encoder(rezult)

        return json_rezult

# #PostSandboxOrder
# @app.get("/snadbox/postsandboxorder/{token}")
# async def read_item(token: str, figi: str, orderdirection: OrderDirection):
#     with Client(token) as client:
#         print("\ntoken = ", token)
#         print("\nfigi = ", figi)
#
#         try:
#             rezult = client.sandbox.post_sandbox_order()
#             print("\nrezult = ", rezult)
#         except Exception as e:
#             print("\nException ", e)
#             rezult = e
#
#         json_rezult = jsonable_encoder(rezult)
#
#         return json_rezult

# PostSandboxOrder
@app.get("/snadbox/postsorder/{token}")
async def read_item(token: str, figi: str, quantity: int, units: int,  nano: int, direction: OrderDirection,
                    account_id: str, order_type: OrderType, order_id: str):
    print("PostSandboxOrder")
    price = {units: units,
             nano: nano}
    with Client(token) as client:
        print("\ntoken = ", token)
        print("figi = ", figi)
        print("quantity = ", quantity)
        print("price = ", price)
        print("direction = ", direction)
        print("account_id = ", account_id)
        print("order_type = ", order_type)
        print("order_id = ", order_id)

        try:
            rezult = client.sandbox.post_sandbox_order(figi=figi, quantity=quantity, price=price, direction=direction,
                                                       account_id=account_id, order_type=order_type, order_id=order_id)
            print("\nrezult = ", rezult)
        except Exception as e:
            print("\nException ", e)
            rezult = e

        json_rezult = jsonable_encoder(rezult)

        return json_rezult


# GetSandboxPortfolio
@app.get("/sandbox/getportfolio/{token}")
async def read_item(token: str, account_id: str):
    print("GetSandboxPortfolio")
    with Client(token) as client:
        print("\ntoken = ", token)
        print("account_id = ", account_id)

        try:
            rezult = client.sandbox.get_sandbox_portfolio(account_id=account_id)
            print("\nrezult = ", rezult)
        except Exception as e:
            print("\nException ", e)
            rezult = e

        json_rezult = jsonable_encoder(rezult)

        return json_rezult


# SandboxPayIn
@app.get("/sandbox/sandboxpayin/{token}")
async def read_item(token: str, account_id: str, currency: str, units: int, nano: int):
    print("SandboxPayIn")
    with Client(token) as client:
        print("\ntoken = ", token)
        print("account_id = ", account_id)

        amount = {"currency": currency,
                  "units": units,
                  "nano": nano}
        print("amount = ", amount)

        try:
            rezult = client.sandbox.sandbox_pay_in(account_id=account_id, amount=amount)
            print("\nrezult = ", rezult)
        except Exception as e:
            print("\nException ", e)
            rezult = e

        json_rezult = jsonable_encoder(rezult)

        return json_rezult
