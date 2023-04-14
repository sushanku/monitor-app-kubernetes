FROM python:3.9

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install python dependencies
copy requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# load sample data
#RUN flask load_data
COPY . .
# gunicorn
# CMD ["/bin/bash", "entrypoint.sh"]

CMD ["gunicorn", "--config", "gunicorn-cfg.py", "run:app"]
