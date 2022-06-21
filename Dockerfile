FROM python:3.10

RUN mkdir /src/
WORKDIR /src/

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY app app

CMD ["python", "-m", "app"]