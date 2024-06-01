FROM python:3.11.8

WORKDIR /app

COPY ./requirements.txt .

RUN python3 -m pip install --upgrade pip

RUN python3 -m pip install -r requirements.txt

ENV PYTHONPATH=/app/code

EXPOSE 8501

CMD []