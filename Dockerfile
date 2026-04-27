FROM python:3.13.11

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD sleep 5; \
    for script in $(ls v*.py | sort -V); \
      do python3 "$script" "$HOST" "$PORT" "$USERNAME" "$PASSWORD" || exit 1; \
    done
