FROM python:3.9-slim

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

ENV app_host=$app_host
ENV app_port=$app_port

EXPOSE $app_port

CMD ["uvicorn", "app.main:app", "--host", app_host, "--port", app_port]
