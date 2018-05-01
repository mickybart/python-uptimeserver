FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY kubeconfig.txt /root/.kube/config

CMD [ "python", "-u", "./run.py" ]

