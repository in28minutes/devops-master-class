DevOps brings Dev and Ops together. Take a look at this graph showing the google trends for Docker and DevOps - Similar timelines.

Why is Docker important for DevOps? Thats what we are going to find out during this section.

In the first few steps, we will install Docker and run a few basic docker commands. This will give us a great perspective on what you can do with Docker. After that, we will talk about 
- What is VM? How is Docker different from a VM? Why is Docker Lightweight?
- How does Docker work? What is the internal architecture of Docker?
- What are the important Docker concepts?

By the end of first 45 minutes of this section, you will understand "Why is Docker important for DevOps?"

Reuse installation steps!

## Second Video

In this step, let's get started with Docker. 

We would want to take a everyday DevOps scenario and see how Docker helps with it.

You are the start developer in a DevOps team and you are working a colleague in the Operations team right now!

Your team is working on three brand new applications - a Java application, a NodeJs application and a Python Application.

All three applications are now ready and you are tasked with working with the operations team to deploy the apps to a QA environment.

You walk down to your operations team colleague and say - hello! we are ready to deploy the applications to QA right now.

You ask him to connect to the QA box and launch up terminal. On windows, you might use a command prompt. 

Launch up terminal or cmd prompt and type this along with me. 

You say, let's start with installing the Java application.

You say "Check if Docker is installed."  docker --version

Awesome. Let's deploy the application. `docker run in28min/todo-rest-api-h2:1.0.0.RELEASE`

Go ahead and run it. You would see a lot of magic happen.

It pulls something. It's downloading something....

In about 20 seconds, the application is launched up.

Your Operations Team Colleague is stunned. 

He asks you, Hey, I see that the application which is running is a Java application but on this machine Java is not installed, How is it running?

In my older projects, I received a document with instructions saying
- Use this Hardware. Install Linux version xyz. On top of it, install Python 3.4.5 or Node a.b.c or Java x.y.z. Install flask a.b or tomcat c.d. Download the app from this repository and then install it using this command. 

I try to follow the instructions to the letter and install the application. In my experience, I face a lot of errors while deploying because the instructions might contain errors or you did not understand them correctly. 

He asks you "How did we deploy this application so easily?"

You want to surprise him. You tell him - "Do you know that you can deploy Node and Python applications exactly the same way with a similar command? The only thing that would change is the name of the name of the repository?"

Your operations team friend is blown away. He says "wow! that's magic".

You tell your friend "Welcome to the world of Docker?". 

I'm sure there are a lot of questions in your mind.

Let's start exploring the magic of Docker further in the next step.

## After next video

How does Docker help DevOps?

Let's start with the three most important features of Docker
- Standardized App Pkg. You create an image. You run the image in the same way irrespective of whether it's a Java app or a Python app.
- Multi Platform Support. Once you create a Docker Image, you can run it any where you have a Docker Engine present.
- Isolation. 
	- You can run one application with Python 2 and another with Python 3 without impacting each other.
	- From Resources Perspective You can configure resources available to each of the containers. 

Why are these features important from a DevOps perspective?
- Standardized Communication - Ops team does not need to worry about what's inside the image? A python app or a Java app? Once an image is created, it can be deployed in the same way.
- Lesser chances of errors! - No need for following an instructions from a document.
- No more "It works in my Local Machine" - 
- Standardized Infrastructure

In this section of the course, we will look at Docker from the perspective of an Operations team 
- Using Dockerfile
- Understanding Docker Image Layers, Caching and Dockerfile
```
docker inspect in28min/hello-world-rest-api:dockerfile1
docker history in28min/hello-world-rest-api:dockerfile1
docker build -t in28min/hello-world-rest-api:dockerfile1 .
```
- Caching of Docker Images - Improve Caching and Being able to run it anywhere!

- Mysql
```
docker run mysql:5.7
docker run --detach --env MYSQL_ROOT_PASSWORD=dummypassword --env MYSQL_USER=todos-user --env MYSQL_PASSWORD=dummytodos --env MYSQL_DATABASE=todos --name mysql --publish 3306:3306 mysql:5.7
mysqlsh
\connect todos-user@localhost:3306
\sql
use todos
select * from todo;

docker run in28min/todo-web-application-mysql:0.0.1-SNAPSHOT

docker container run -p 8080:8080 --link=mysql -e RDS_HOSTNAME=mysql  in28min/todo-web-application-mysql:0.0.1-SNAPSHOT

docker network ls
docker inspect bridge #after running mysql and web app
docker inspect host (--network=host) Works in Unix - Not supported in Docker Deskop. Host is Virtual Machines.

### Host Networking in Docker for Mac

- https://docs.docker.com/network/host/

>The host networking driver only works on Linux hosts, and is not supported on Docker Desktop for Mac, Docker Desktop for Windows, or Docker EE for Windows Server.

docker network ls
docker network create web-application-mysql-network
docker inspect web-application-mysql-network

docker container run -p 8080:8080 --network=web-application-mysql-network -e RDS_HOSTNAME=mysql  in28min/todo-web-application-mysql:0.0.1-SNAPSHOT

docker run --detach --env MYSQL_ROOT_PASSWORD=dummypassword --env MYSQL_USER=todos-user --env MYSQL_PASSWORD=dummytodos --env MYSQL_DATABASE=todos --name mysql --publish 3306:3306 --network=web-application-mysql-network mysql:5.7

docker container prune

docker run --detach --env MYSQL_ROOT_PASSWORD=dummypassword --env MYSQL_USER=todos-user --env MYSQL_PASSWORD=dummytodos --env MYSQL_DATABASE=todos --name mysql --publish 3306:3306 --network=web-application-mysql-network --volume mysql-database-volume:/var/lib/mysql  mysql:5.7


docker-compose up
docker-compose up -d
docker-compose scale currency-conversion-service=2
docker-compose logs
docker-compose logs -f
