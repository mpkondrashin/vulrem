# VulRem - Vulnerability Remediaton
# (c) 2020 by Mikhail Kondrashin mkondrashin@gmail.com
FROM python:3.11.0b1-slim-bullseye
RUN pip install requests docker-image-py
RUN pip install https://automation.deepsecurity.trendmicro.com/sdk/20_0/v1/dsm-py-sdk.zip
COPY *.py /app/
CMD python /app/main.py
