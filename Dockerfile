FROM python:3.10

# Set environment variables.
ENV PYTHONWRITEBYTECODE 1
ENV PYTHONBUFFERED 1

# Set working directory.
WORKDIR /code

# Copy dependencies.
COPY ./requirements.txt /code/requirements.txt

# Install dependencies.
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy project.
COPY ./app /code/app

EXPOSE 8000

ENTRYPOINT [ "gunicorn", "app.main:app", "--workers", "2", "--worker-class", \
        "uvicorn.workers.UvicornWorker",  "-b", "0.0.0.0:8000" ]