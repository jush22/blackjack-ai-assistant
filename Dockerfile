FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y libgl1 libglib2.0-0
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY functions.py .
COPY percent_engine.py .
COPY best.pt .
COPY live_vision.py .
CMD ["python3", "live_vision.py"]