FROM python:3.13.7-trixie

WORKDIR /

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Cache buster to force rebuild of app layer
RUN echo "Build at $(date)"

COPY app /app

# Set PYTHONPATH so app module can be found
ENV PYTHONPATH=/


#ENV PATH="/app/.venv/bin:$PATH"

#RUN mkdir -p /app/static /app/templates
#COPY templates/ /app/templates/

#CMD gunicorn --workers=1 --worker-class=uvicorn.workers.UvicornWorker --bind=localhost:8001 app.main:app