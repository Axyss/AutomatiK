FROM python:3.12.3-slim
WORKDIR /data
ADD . .
RUN pip3 install --no-cache-dir -r requirements.txt
CMD ["python3", "-u", "-m", "automatik.bot"]