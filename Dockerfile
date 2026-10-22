FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOST=0.0.0.0 \
    PORT=5000
WORKDIR /opt/cloud-app
RUN useradd --create-home --uid 10001 appuser
COPY requirements.txt ./
RUN python -m pip install --no-index --no-cache-dir -r requirements.txt
COPY --chown=appuser:appuser app/ ./app/
USER appuser
EXPOSE 5000
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import os,urllib.request; urllib.request.urlopen('http://127.0.0.1:'+os.environ.get('PORT','5000')+'/health',timeout=2)"
CMD ["python", "-m", "app.main"]
