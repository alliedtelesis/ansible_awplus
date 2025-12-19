FROM python:3.13-slim

ENV DEBIAN_FRONTEND=noniteractive

RUN apt-get update && \
	apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
		build-essential \
    	python3 \
    	python3-venv \
		python3-dev \
   		python3-pip \
    	git \
		libssh-dev \
		ssh && \
    apt-get clean && \
	rm -rf /var/lib/apt/lists/*

COPY . /ansible_collections/alliedtelesis/awplus
WORKDIR /ansible_collections/alliedtelesis/awplus

RUN pip install --upgrade pip && \
    pip install --upgrade -i https://pypi.atlnz.lc/atlnz/pypi/+simple/ -r ./integration_test/requirements.txt \
	pip install ansible==12.2.0
