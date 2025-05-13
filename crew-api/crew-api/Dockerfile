FROM python:3.11-slim

WORKDIR /app
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port and start the server
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]