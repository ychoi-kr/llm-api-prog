FROM python:3-alpine

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

ENV OPENAI_API_KEY=${OPENAI_API_KEY}

CMD ["python", "main.py"]