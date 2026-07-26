# The base image: a slim Python 3.11.
FROM python:3.11-slim

WORKDIR /app

# Copy the dependency list FIRST and install it, before copying the
# source. Docker caches each step, so editing your Python code no
# longer re-installs every package — rebuilds take seconds instead
# of minutes. Reverse these two blocks and you lose that entirely.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Now the source.
COPY . .

# --host 0.0.0.0 is REQUIRED. By default uvicorn listens only on
# 127.0.0.1, which inside a container means "this container only" —
# nothing outside could reach it, including your browser.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]