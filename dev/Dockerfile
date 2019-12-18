FROM ubuntu:18.04

# Set the locale
ENV LANG C.UTF-8  
ENV LC_ALL C.UTF-8 

RUN apt-get update -y && \
    apt-get install -y python3 python3-dev python3-pip

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt

WORKDIR /app
COPY . /app

RUN pip3 install -r requirements.txt

# ENTRYPOINT [ "flask" ]
# CMD [ "run" ]
EXPOSE 5000/tcp