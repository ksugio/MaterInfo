FROM python:3.11

# install libralies
RUN apt update
RUN apt upgrade -y
RUN apt install vim -y
RUN apt install libgl1-mesa-dev -y
RUN apt install redis-server -y

# copy files
RUN mkdir /MaterInfo
WORKDIR /MaterInfo
COPY ./ /MaterInfo

# install python libralies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt