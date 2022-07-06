FROM python:3.8-alpine
WORKDIR /automatik
ADD . .
RUN pip3 install --no-cache-dir -r requirements.txt
CMD ["python3", "-u", "main.py"]