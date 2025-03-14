FROM python:3.11

RUN mkdir /logger
WORKDIR /logger
COPY cpu.py /logger

RUN pip install --upgrade pip
RUN pip install redis
RUN pip install psutil