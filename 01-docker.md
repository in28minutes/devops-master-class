# Getting Started with Docker

## Commands

```
docker --version

docker run in28min/todo-rest-api-h2:1.0.0.RELEASE
docker run -p 5000:5000 in28min/todo-rest-api-h2:1.0.0.RELEASE
docker run -p 5000:5000 -d in28min/todo-rest-api-h2:1.0.0.RELEASE
docker logs b18f7dd024401334f9193808dc9e9a8f5abbd3ab1c9c45934e10d7157570759e
docker logs -f b18f7dd024401334f9193808dc9e9a8f5abbd3ab1c9c45934e10d7157570759e
docker container ls
docker run -p 5001:5000 -d in28min/todo-rest-api-h2:1.0.0.RELEASE

docker images
docker images prune
docker container prune
docker container ls -a
docker container stop c52d0a12eada
docker run -d -p 5001:5000 in28min/todo-rest-api-h2:0.0.1-SNAPSHOT
docker system prune -a

docker tag in28min/todo-rest-api-h2:1.0.0.RELEASE in28min/todo-rest-api-h2:latest
docker pull mysql
docker search mysql
docker images
docker image history f8049a029560
docker image inspect f8049a029560
docker image remove mysql
docker images

docker container pause c7
docker container unpause c7
docker container inspect c7
docker container stop c7
docker container kill c7

docker events
docker container run -p 5000:5000 -d --restart=always in28min/todo-rest-api-h2:1.0.0.RELEASE
docker container ls
docker top 8ab
docker stats
docker container run -p 5000:5000 -m 512m --cpu-quota 5000 -d  in28min/todo-rest-api-h2:1.0.0.RELEASE
docker container run -p 5000:5000 -m 512m --cpu-quota 50000 -d  in28min/todo-rest-api-h2:1.0.0.RELEASE
docker system df
```

### REST API Application

https://hub.docker.com/r/in28min/todo-rest-api-h2

### Web Application SQL

https://hub.docker.com/r/in28min/todo-web-application-mysql

Todo Management Application to Add, delete and update your todos
- URL - http://localhost:8080/login 
- Credentials - `in28minutes`/`dummy`

Talks with a MySQL Database

Environment Variables:
- RDS_HOSTNAME: mysql
- RDS_PORT: 3306
- RDS_DB_NAME: todos
- RDS_USERNAME: todos-user
- RDS_PASSWORD: dummytodos

### Docker Compose Example

```
version: '3.7'
# Removed subprocess.CalledProcessError: Command '['/usr/local/bin/docker-credential-desktop', 'get']' returned non-zero exit status 1
# I had this:
# cat ~/.docker/config.json
# {"auths":{},"credsStore":"", "credsStore":"desktop","stackOrchestrator":"swarm"}
# I updated to this:
# {"auths":{},"credsStore":"","stackOrchestrator":"swarm"}
services:
  todo-web-application:
    image: in28min/todo-web-application-mysql:0.0.1-SNAPSHOT
    #build:
      #context: .
      #dockerfile: Dockerfile
    ports:
      - "8080:8080"
    restart: always
    depends_on: # Start the depends_on first
      - mysql 
    environment:
      RDS_HOSTNAME: mysql
      RDS_PORT: 3306
      RDS_DB_NAME: todos
      RDS_USERNAME: todos-user
      RDS_PASSWORD: dummytodos
    networks:
      - todo-web-application-network

  mysql:
    image: mysql:5.7
    ports:
      - "3306:3306"
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_ROOT_PASSWORD: dummypassword 
      MYSQL_USER: todos-user
      MYSQL_PASSWORD: dummytodos
      MYSQL_DATABASE: todos
    volumes:
      - mysql-database-data-volume:/var/lib/mysql
    networks:
      - todo-web-application-network  
  
# Volumes
volumes:
  mysql-database-data-volume:

networks:
  todo-web-application-network:
```

## Next Steps


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

```
