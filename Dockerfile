# VulRem - Vulnerability Remediator
# (c) 2020 by Mikhail Kondrashin
FROM python:3.8
RUN pip install requests docker-image-py
RUN pip install https://automation.deepsecurity.trendmicro.com/sdk/20_0/v1/dsm-py-sdk.zip
COPY *.py /app/
CMD python /app/main.py
