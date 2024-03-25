from app.main import app
import uvicorn
import os


try:
    app_host = os.environ['app_host']
except:
    app_host = '127.0.0.2'

try:
    app_port = int(os.environ['app_port'])
except:
    app_port = 8080


if __name__ == '__main__':
    uvicorn.run(app, port=app_port, host=app_host)