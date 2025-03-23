FROM python:3.11.4-slim-buster
WORKDIR /automatik-root
ADD . .
RUN pip3 install --no-cache-dir -r requirements.txt
CMD ["python3", "-u", "-m", "automatik.bot"]