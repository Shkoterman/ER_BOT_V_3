FROM python

WORKDIR /ER_BOT

COPY . .

RUN pip install --user --upgrade pip
RUN pip install --no-cache-dir --user -r requirements.txt

VOLUME ["/ER_BOT/regCheck/data"]

CMD ["python", "main.py"]
