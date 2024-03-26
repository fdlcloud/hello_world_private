FROM python:3.9-slim-bullseye

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

#ENV app_host=$app_host
#ENV app_port=$app_port
#ENV openai_key=$openai_key

#EXPOSE $app_port
EXPOSE 50505

#CMD ["uvicorn", "app.main:app", "--host", app_host, "--port", app_port, '--openai_key', openai_key]
#CMD ["uvicorn", "app.main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "80"]
ENTRYPOINT ["gunicorn", "app.main:app"]
