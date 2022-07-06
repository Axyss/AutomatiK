FROM python:3.9.13-slim-buster
WORKDIR /automatik
ADD . .
RUN pip3 install --no-cache-dir -r requirements.txt
CMD ["python3", "-u", "main.py"]