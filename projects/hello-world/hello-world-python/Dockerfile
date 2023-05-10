# Alpine here is called base image
FROM python:alpine3.10  

# Specify the working directory
WORKDIR /app  

 # Copy all files from current directory to working directory
COPY . /app

# Mention all requirements here and run this file
RUN pip install -r requirements.txt

# On what port we want to expose this application
EXPOSE 5000

# Command to run the application
CMD python ./launch.py

#COPY requirements.txt /app/requirements.txt
#ENTRYPOINT ["python", "./launch.py"]
