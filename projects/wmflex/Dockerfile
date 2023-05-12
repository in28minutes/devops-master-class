# Slim version of Python
FROM python:3.8.12-slim

# Download Package Information
RUN apt-get update -y

# Install Tkinter
RUN apt-get install tk -y

# Commands to run Tkinter application
# CMD ["/app/tkinter_app.py"]
# ENTRYPOINT ["python3"]

# Copying the main app after port has been expose. This is done to make sure that the top layer
# get to use cache wheever possible. Most of the code changes would happen in the
# app code only, hence adding it here.
COPY . /app
CMD python ./wingman.py

#COPY requirements.txt /app/requirements.txt
#ENTRYPOINT ["python", "./wingman.py"]
