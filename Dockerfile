FROM python:3.13.7-trixie

WORKDIR /

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app /app



#ENV PATH="/app/.venv/bin:$PATH"

#RUN mkdir -p /app/static /app/templates
#COPY templates/ /app/templates/

#CMD gunicorn --workers=1 --worker-class=uvicorn.workers.UvicornWorker --bind=localhost:8001 app.main:app