FROM python:3.8.6-buster

RUN python -m pip install --upgrade pip

ENV PYTHONPATH="/pymodules/spy:${PYTHONPATH}"

WORKDIR /tmp

COPY ./requirements.txt .

RUN pip install -r requirements.txt

COPY ./src /pymodules/spy

COPY ./bin/spy /usr/bin/spy
COPY ./bin/spycollect /usr/bin/spycollect
