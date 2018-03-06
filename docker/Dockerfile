FROM python:3

ARG UPTIME_ENV

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY kubeconfig.txt /root/.kube/config

ENV UPTIME_ENV ${UPTIME_ENV:-local}
CMD [ "python", "-u", "./run.py" ]

