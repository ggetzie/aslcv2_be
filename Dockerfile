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
ENV APP_HOME=/usr/local/src/aslcv2_be
RUN mkdir -p $APP_HOME/staticfiles

# Set the working directory 
WORKDIR $APP_HOME

COPY requirements.txt $APP_HOME

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the current directory contents into the container 
ADD . $APP_HOME
RUN mkdir -p $APP_HOME/logs/email
RUN touch $APP_HOME/logs/debug.log
RUN touch $APP_HOME/logs/gunicorn_supervisor.log

RUN chown -R aslcv2_be_user:webapps $APP_HOME
USER aslcv2_be_user:webapps

ENTRYPOINT ["sh", "/usr/local/src/aslcv2_be/entrypoint.sh"]