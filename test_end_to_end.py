from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest


app = FastAPI()
client = TestClient(app)


@pytest.fixture
def e_to_e_example():
    run_first_call = False
    try:
        response = client.get("/")
        if response.status_code == 200:
            run_first_call = response.json() == {"msg": "Hello World"}
    except:
        run_first_call = False

    run_second_call = False
    try:
        response = client.get("/")
        if response.status_code == 200:
            run_second_call = response.json() == {"msg": "Hello World"}
    except:
        run_second_call = False

    all_calls = run_first_call and run_second_call

    assert all_calls == True