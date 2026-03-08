FROM python:3.12

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements/base.txt /tmp/base.txt

RUN pip install --upgrade pip
RUN pip install -r /tmp/base.txt

COPY . /app
