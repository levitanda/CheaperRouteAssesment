FROM python:3.9-slim
WORKDIR /app
EXPOSE 8000
CMD ["tail", "-f", "/dev/null"]
