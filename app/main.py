from typing import Union
from fastapi import FastAPI, HTTPException
import httpx
from pydantic import BaseModel
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.encoders import jsonable_encoder
from azure import identity
import os
import requests
import pyodbc
import struct
import openai

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

@app.get("/home", response_class=HTMLResponse)
async def read_items():
    return """
        <html lang="en" data-bs-theme="light">
        
            <head>
            <script src="/docs/5.3/assets/js/color-modes.js"></script>

            <script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@3.3.7/dist/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@3.3.7/dist/css/bootstrap-theme.min.css" integrity="sha384-rHyoN1iRsVXV4nD0JutlnGaslCJuC7uwjduW9SVrLvRYooPp2bWYgmgJQIXwl/Sp" crossorigin="anonymous">
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@3.3.7/dist/js/bootstrap.min.js" integrity="sha384-Tc5IQib027qvyjSMfHjOMaLkfuWVxZxUPnCJA7l2mCWNIpG9mGCD8wGNIcPD7Txa" crossorigin="anonymous"></script>
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-ho+j7jyWK8fNQe+A12Hb8AhRq26LrZ/JpcUGGOn+Y7RsweNrtN/tE3MoK7ZeZDyx" crossorigin="anonymous"></script>
            <script src="https://cdn.jsdelivr.net/npm/checkout@1.0.1/lib/index.min.js"></script>

            <link rel="apple-touch-icon" href="/docs/5.3/assets/img/favicons/apple-touch-icon.png" sizes="180x180">
            <link rel="icon" href="/docs/5.3/assets/img/favicons/favicon-32x32.png" sizes="32x32" type="image/png">
            <link rel="icon" href="/docs/5.3/assets/img/favicons/favicon-16x16.png" sizes="16x16" type="image/png">
            <link rel="manifest" href="/docs/5.3/assets/img/favicons/manifest.json">
            <link rel="mask-icon" href="/docs/5.3/assets/img/favicons/safari-pinned-tab.svg" color="#712cf9">
            <link rel="icon" href="/docs/5.3/assets/img/favicons/favicon.ico">
            
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <meta name="description" content="">
            <meta name="author" content="Mark Otto, Jacob Thornton, and Bootstrap contributors">
            <meta name="generator" content="Hugo 0.122.0">

            <title>Checkout example · Bootstrap v5.3</title>
            
            <link rel="canonical" href="https://getbootstrap.com/docs/5.3/examples/checkout/">
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@docsearch/css@3">
        
            <meta name="theme-color" content="#712cf9">
        
                <style>
                  .bd-placeholder-img {
                    font-size: 1.125rem;
                    text-anchor: middle;
                    -webkit-user-select: none;
                    -moz-user-select: none;
                    user-select: none;
                  }
            
                  @media (min-width: 768px) {
                    .bd-placeholder-img-lg {
                      font-size: 3.5rem;
                    }
                  }
            
                  .b-example-divider {
                    width: 100%;
                    height: 3rem;
                    background-color: rgba(0, 0, 0, .1);
                    border: solid rgba(0, 0, 0, .15);
                    border-width: 1px 0;
                    box-shadow: inset 0 .5em 1.5em rgba(0, 0, 0, .1), inset 0 .125em .5em rgba(0, 0, 0, .15);
                  }
            
                  .b-example-vr {
                    flex-shrink: 0;
                    width: 1.5rem;
                    height: 100vh;
                  }
            
                  .bi {
                    vertical-align: -.125em;
                    fill: currentColor;
                  }
            
                  .nav-scroller {
                    position: relative;
                    z-index: 2;
                    height: 2.75rem;
                    overflow-y: hidden;
                  }
            
                  .nav-scroller .nav {
                    display: flex;
                    flex-wrap: nowrap;
                    padding-bottom: 1rem;
                    margin-top: -1px;
                    overflow-x: auto;
                    text-align: center;
                    white-space: nowrap;
                    -webkit-overflow-scrolling: touch;
                  }
            
                  .btn-bd-primary {
                    --bd-violet-bg: #712cf9;
                    --bd-violet-rgb: 112.520718, 44.062154, 249.437846;
            
                    --bs-btn-font-weight: 600;
                    --bs-btn-color: var(--bs-white);
                    --bs-btn-bg: var(--bd-violet-bg);
                    --bs-btn-border-color: var(--bd-violet-bg);
                    --bs-btn-hover-color: var(--bs-white);
                    --bs-btn-hover-bg: #6528e0;
                    --bs-btn-hover-border-color: #6528e0;
                    --bs-btn-focus-shadow-rgb: var(--bd-violet-rgb);
                    --bs-btn-active-color: var(--bs-btn-hover-color);
                    --bs-btn-active-bg: #5a23c8;
                    --bs-btn-active-border-color: #5a23c8;
                  }
            
                  .bd-mode-toggle {
                    z-index: 1500;
                  }
            
                  .bd-mode-toggle .dropdown-menu .active .bi {
                    display: block !important;
                  }
                </style>
            
              <style>
            .fortipam-fade-in {
              opacity: 0;
              animation: fortipam-fade-in-animation 0.15s ease-in forwards;
            }
            
            @keyframes fortipam-fade-in-animation {
              from {
                opacity: 0;
              }
            
              to {
                opacity: 1;
              }
            }</style>
        </head>
      <body class="bg-body-tertiary">
            
        <div class="container">
          <main>
            <div class="py-5 text-center">
              <h2>App Test AKS</h2>
            </div>
        
              <div class="col-md-7 col-lg-8">

                  <div class="row gy-12">
                    <div class="col-md-12">
                      <label for="cc-expiration" class="form-label">Test Things</label>
                      <input type="text" class="form-control" id="cc-expiration" placeholder="" required="">
                    </div>
                  </div>

                  <div class="row gy-12">
                    <div class="col-md-12">
                      <label for="cc-done" class="form-label">Output Things</label>
                      <input type="text" class="form-control" id="cc-done" placeholder="" required="">
                    </div>
                  </div>
        
                  <hr class="my-4">
        
                  <button id="myButton" class="w-100 btn btn-primary btn-lg">Do Enrich</button>

              </div>
            </div>
          </main>
        
        </div>
        
        <script>
        function sendData() {
            $.ajax({
                url: '/output_text', // The URL to which the request is sent
                type: 'POST', // The type of request to make, e.g., "POST", "GET"
                contentType: 'application/json', // The content type of the data sent to the server
                data: JSON.stringify({
                    text_to_enrich: $('#cc-expiration').val(),
                }),
                success: function(response) {
                    $('#cc-done').val(response['enriched_text']);
                },
                error: function(xhr, status, error) {
                    // This function is called if the request fails
                    // 'xhr' is the XMLHttpRequest object
                    console.log('Error:', xhr, status, error);
                }
            });
        };
        
        $(document).ready(function() {
            $('#myButton').click(sendData);
        });
        
        </script>
        </body>
        </html>
    """

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


class TextEnr(BaseModel):
    text_to_enrich: str

@app.post("/output_text")
def output_text(q: TextEnr):
    text_to_enr = q.text_to_enrich
    try:
        try:
            from secrets import openai_key
            os.environ['openai_key'] = openai_key
        except:
            pass

        from openai import OpenAI
        client = OpenAI(api_key=os.environ.get("openai_key"))

        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
                {"role": "user", "content": "Riddle me something: %s" % text_to_enr}
            ]
        )

        out_out = completion.choices[0].message.content
    except:
        out_out = 'AAAAAAAAA' + text_to_enr

    json_compatible_item_data = jsonable_encoder({'enriched_text': out_out})

    return JSONResponse(content=json_compatible_item_data, status_code=200)


@app.put("/other_items/{item_id}")
def update_item(item: Item):
    return {"item": item}


@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}

