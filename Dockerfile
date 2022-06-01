# syntax=docker/dockerfile:1
FROM python:3.9
WORKDIR /Receipts_book
COPY requirements.txt /Receipts_book/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /Receipts_book/requirements.txt
COPY ./app /Receipts_book/app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]