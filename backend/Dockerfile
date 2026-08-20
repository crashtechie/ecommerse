FROM debian:trixie-slim

RUN apt-get update && apt-get install -y \
    python3 \
    python3-venv \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv "$VIRTUAL_ENV"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache -r requirements.txt

COPY . .

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
