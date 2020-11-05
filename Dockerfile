##########
# BUILDER #
###########

# pull official base image
FROM python:3.8.0-alpine as builder

WORKDIR /usr/src/landbank
# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# install psycopg2 dependencies
RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev libffi-dev

# lint
RUN pip install --upgrade pip
RUN pip install flake8
COPY . /usr/src/landbank/

# install dependencies
COPY ./requirements.txt .
RUN ls /usr/src/landbank
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/landbank/wheels -r requirements.txt
RUN ls -al /usr/src/landbank/wheels


#########
# FINAL #
#########

# pull official base image
FROM python:3.8.0-alpine

# create directory for the app user
RUN mkdir -p /home/landbank

# create the app user
RUN addgroup -S landbank && adduser -S landbank -G landbank


# create the appropriate directories
ENV HOME=/home/landbank
ENV APP_HOME=/home/landbank/web
RUN mkdir $APP_HOME
RUN mkdir $APP_HOME/staticfiles
RUN mkdir $APP_HOME/media
WORKDIR $APP_HOME

# install dependencies
RUN apk update \
        && apk add postgresql-dev libpq gcc python3-dev musl-dev libffi-dev
COPY --from=builder /usr/src/landbank/wheels/ wheels
COPY --from=builder /usr/src/landbank/requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache ./wheels/*

# copy entrypoint-prod.sh
COPY ./entrypoint.sh $APP_HOME
# copy project
COPY . $APP_HOME
# chown all the files to the app user
RUN chown -R landbank:landbank $APP_HOME
# change to the app user
USER landbank

# run entrypoint.sh
ENTRYPOINT ["/home/landbank/web/entrypoint.sh"]
