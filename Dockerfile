# The first instruction is what image we want to base our container on
# We Use an official Python runtime as a parent image
FROM python:3.8

EXPOSE 8009
RUN groupadd webapps
RUN useradd --system --gid webapps aslcv2_be_user

# The enviroment variable ensures that the python output is set straight
# to the terminal with out buffering it first
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# create root directory for our project in the container
RUN mkdir -p /usr/local/src/aslcv2_be

# Set the working directory 
WORKDIR /usr/local/src/aslcv2_be

# Copy the current directory contents into the container 
ADD . /usr/local/src/aslcv2_be/

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt