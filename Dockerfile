FROM ubuntu:18.10
ENV LANG C.UTF-8

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y \
    build-essential \
    ca-certificates \
    gcc \
    git \
    libpq-dev \
    make \
    python-pip \
    python2.7 \
    python2.7-dev \
    ssh \
    && apt-get autoremove \
    && apt-get clean

RUN pip install -U "setuptools"
RUN pip install -U "pip"
RUN pip install -U "Mercurial"
RUN pip install -U "virtualenv"
RUN pip install -U "requests[security]==2.18.4"
RUN pip install -U "beautifulsoup4==4.6.0"
RUN pip install -U "lxml"

COPY . /root
WORKDIR /root
CMD ["/usr/bin/python2.7", "yzuSurvey.py"]
