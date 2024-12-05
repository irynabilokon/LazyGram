FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

COPY .env /app/.env

EXPOSE $PORT

COPY vertex_ai_apikey.json /app/vertex_ai_apikey.json

ENV GOOGLE_APPLICATION_CREDENTIALS="/app/vertex_ai_apikey.json"

RUN echo '#!/bin/bash\nset -e\nstreamlit run app_medium.py --server.port $PORT --server.address 0.0.0.0' > run.sh && \
    chmod +x run.sh

HEALTHCHECK CMD curl --fail http://localhost:$PORT/_stcore/health || exit 1

CMD ["./run.sh"]
