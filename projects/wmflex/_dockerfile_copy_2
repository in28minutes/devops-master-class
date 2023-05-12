FROM python:2.7.15-alpine
RUN apk add --no-cache zlib-dev
RUN apk add --no-cache linux-headers
RUN apk add --no-cache gcc python2-dev
RUN apk add --no-cache --virtual .build-deps build-base \
    && apk add --no-cache jpeg-dev
RUN apk add --no-cache gcc musl-dev
RUN apk update && apk add --no-cache tcl tk
RUN apk add --update --no-cache --virtual .build-deps gcc musl-dev
RUN apk del .build-deps
ENV DISPLAY=:0.0
# ENV DISPLAY=:0.0
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 5000

# Copying the main app after port has been expose. This is done to make sure that the top layer
# get to use cache wheever possible. Most of the code changes would happen in the
# app code only, hence adding it here.
COPY . /app
CMD python ./wingman.py

#COPY requirements.txt /app/requirements.txt
#ENTRYPOINT ["python", "./wingman.py"]
