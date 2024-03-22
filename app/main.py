from typing import Union
from fastapi import FastAPI, HTTPException
import httpx
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from azure import identity
import os
import requests
import pyodbc
import struct

app = FastAPI()

# ENV AZURE_SQL_CONNECTIONSTRING: AZURE_SQL_CONNECTIONSTRING='Driver={ODBC Driver 18 for SQL Server};Server=tcp:<database-server-name>.database.windows.net,1433;Database=<database-name>;UID=<user-name>;PWD=<user-password>;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30'
os.environ['AZURE_SQL_CONNECTIONSTRING'] = 'Driver={ODBC Driver 18 for SQL Server};Server=tcp:<database-server-name>.database.windows.net,1433;Database=<database-name>;UID=<user-name>;PWD=<user-password>;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30'
connection_string = os.environ["AZURE_SQL_CONNECTIONSTRING"]

# https://learn.microsoft.com/en-us/azure/azure-sql/database/azure-sql-python-quickstart?view=azuresql&tabs=windows%2Csql-auth


def get_azure_db_conn():
    credential = identity.DefaultAzureCredential(exclude_interactive_browser_credential=False)
    token_bytes = credential.get_token("https://database.windows.net/.default").token.encode("UTF-16-LE")
    token_struct = struct.pack(f'<I{len(token_bytes)}s', len(token_bytes), token_bytes)
    SQL_COPT_SS_ACCESS_TOKEN = 1256  # This connection option is defined by microsoft in msodbcsql.h
    conn = pyodbc.connect(connection_string, attrs_before={SQL_COPT_SS_ACCESS_TOKEN: token_struct})
    return conn


def read_from_azure_db(item_first_name, item_last_name):
    try:
        with get_azure_db_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO PersonsTable (FirstName, LastName) VALUES (%s, %s)" % (item_first_name, item_last_name))
            conn.commit()
            conn.close()
        return 'Success'
    except:
        return 'Fail'


class Person(BaseModel):
    first_name: str
    last_name: Union[str, None]


class ResponsePerson(BaseModel):
    first_name: str
    last_name: Union[str, None]


@app.post("/person", response_model=ResponsePerson)
def create_person(item: Person):
    read_from_azure_db(item.first_name, item.last_name)
    return JSONResponse(item)


class TicketRetrieval(BaseModel):
    session_id: str
    user_id: str
    ticket_serial_number: str


@app.post("/update_service_now_ticket")
def update_service_now_ticket(ticket: TicketRetrieval):
    try:
        url = get_external_endpoint_name('service_now_endpoint_example')
        params = dict(
            session_id=ticket.session_id,
            user_id=ticket.user_id,
            ticket_serial_number=ticket.ticket_serial_number,
        )
        response = requests.post(url=url, params=params)
        data = response.json()
        return JSONResponse(data, status_code=200)
    except:
        # what is supposed to happen here?
        return JSONResponse({'Error': 'Mistake'}, status_code=200)


def fetch_data_from_api_general():
    """Fetches data from a given API endpoint."""
    import requests
    endpoint_url = "https://fakeapi.com/data"
    response = requests.get(endpoint_url)
    print(response.status_code)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def get_external_endpoint_name(endpoint_name):
    import yaml
    with open("data.yaml", 'r') as stream:
        return yaml.safe_load(stream)[endpoint_name]


class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None


def post_data_to_api(endpoint_url, json_data):
    """Sends data to a given API endpoint via POST request."""
    response = requests.post(endpoint_url, json=json_data)
    if response.status_code == 200:
        return response.json()
    else:
        return None


async def get_weather_async(city: str) -> dict:
    """Mockable function to get weather from an external service."""
    url = f"https://example-weather-service.com/weather/{city}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="Weather data not found")
        return response.json()

@app.get("/async_weather/{city}")
async def weather_async(city: str):
    return await get_weather_async(city)


def get_weather(city: str) -> dict:
    """Mockable function to get weather from an external service."""
    url = f"https://example-weather-service.com/weather/{city}"
    response = requests.get(url)
    if response.status_code != 200:
        raise HTTPException(status_code=404, detail="Weather data not found")
    print('ciao')
    return JSONResponse(response.json())


@app.get("/weather/{city}")
def weather(city: str):
    return get_weather(city)

@app.get("/root")
def read_root():
    return JSONResponse({"msg": "Hello World"})


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.post("/generic_item_request")
def read_item(q: Union[str, None] = None):
    item = {
        'name': q.name,
        'price': q.price,
        'is_offer': q.is_offer,
    }
    json_compatible_item_data = jsonable_encoder(item)
    return JSONResponse(content=json_compatible_item_data, status_code=200)


@app.put("/other_items/{item_id}")
def update_item(item: Item):
    return {"item": item}


@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}

