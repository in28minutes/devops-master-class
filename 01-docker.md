# Getting Started with Docker

## Commands

```
511  docker --version
  512  docker run in28min/todo-rest-api-h2:1.0.0.RELEASE
  513  docker run in28min/todo-rest-api-h2:1.0.0.RELEASE
  514  docker run in28min/todo-rest-api-h2:1.0.0.RELEASE
  515  docker run -un -p 5000:5000 in28min/todo-rest-api-h2:1.0.0.RELEASE
  516  docker run -p 5000:5000 in28min/todo-rest-api-h2:1.0.0.RELEASE
  517  docker run -d -p 5000:5000 in28min/todo-rest-api-h2:1.0.0.RELEASE
  518  docker logs b18f7dd024401334f9193808dc9e9a8f5abbd3ab1c9c45934e10d7157570759e
  519  docker logs -f b18f7dd024401334f9193808dc9e9a8f5abbd3ab1c9c45934e10d7157570759e
  520  docker container ls
  521  docker run -d -p 5001:5000 in28min/todo-rest-api-h2:1.0.0.RELEASE
  522  docker images
  523  docker prune
  524  docker images prune
  525  docker images
  526  docker containers prune
  527  docker container prune
  528  docker container ls -a
  529  docker container stop c52d0a12eada
  530  docker container stop d7d8b040d684
  531  docker container stop 9cbe69912507
  532  docker container stop b18f7dd02440
  533  clear
  534  docker container ls -a
  535  docker container prune
  536  docker images
  537  docker run -d -p 5001:5000 in28min/todo-rest-api-h2:0.0.1-SNAPSHOT
  538  docker run -d -p 5001:5000 in28min/todo-rest-api-h2:0.0.1-SNAPSHOT
  539  docker images
  540  docker system prune -a
  541  docker run -d -p 5001:5000 in28min/todo-rest-api-h2:0.0.1-SNAPSHOT
  542  docker container ls
  543  docker container stop 79
  544  docker system prune -a
  545  docker run -d -p 5001:5000 in28min/todo-rest-api-h2:0.0.1-SNAPSHOT
  546  docker run -d -p 5001:5000 in28min/todo-rest-api-h2:1.0.0.RELEASE
  547  docker images
  548  docker tag in28min/todo-rest-api-h2:1.0.0.RELEASE in28min/todo-rest-api-h2:lates
  549  docker tag in28min/todo-rest-api-h2:1.0.0.RELEASE in28min/todo-rest-api-h2:latest
  550  docker images
  551  docker images remove in28min/todo-rest-api-h2:lates
  552  docker image remove in28min/todo-rest-api-h2:lates
  553  docker images
  554  docker pull mysql
  555  docker search mysql
  556  docker images
  557  docker image history f8049a029560
  558  docker image inspect f8049a029560
  559  docker image remove mysql
  560  docker images
  561  docker container run -d -p 5000:5000 in28min/todo-rest-api-h2:1.0.0.RELEASE
  562  docker container pause c7
  563  docker container unpause c7
  564  docker container inspect c7
  565  docker container ls -a
  566  docker container prune 
  567  docker container ls -a
  568  docker container logs -f c7
  569  docker container run -d -p 5000:5000 in28min/todo-rest-api-h2:1.0.0.RELEASE
  570  docker container stop c7
  571  docker container kill c7
  572  docker container ls
  573  docker container stop ca
  574  docker container ls -a
  575  docker container prune -a
  576  docker container prune
  577  docker container run -d -p 5000:5000 --restart=always in28min/todo-rest-api-h2:1.0.0.RELEASE
  578  docker container stop 07fa
  579  docker container ls -a
  580  docker container ls -a
  581  docker container stop 07f
  582  docker container prune
  583  docker events
  584  docker containers ls
  585  docker container ls
  586  docker container run -d -p 5000:5000 --restart=always in28min/todo-rest-api-h2:1.0.0.RELEASE
  587  docker top
  588  docker container ls
  589  docker top 8ab
  590  docker stats
  591  docker container run -p 5000:5000 -m 512m --cpu-quota 5000 -d  in28min/todo-rest-api-h2:1.0.0.RELEASE
  592  docker container ls
  593  docker container stop 8a
  594  docker container run -p 5000:5000 -m 512m --cpu-quota 5000 -d  in28min/todo-rest-api-h2:1.0.0.RELEASE
  595  docker container logs c6
  596  docker container logs -f c6
  597  docker container ls
  598  docker container stop c6
  599  docker container run -p 5000:5000 -m 512m --cpu-quota 50000 -d  in28min/todo-rest-api-h2:1.0.0.RELEASE
  600  docker container logs -f 8b
  601  docker system df
  602  docker container
  603  docker container ls
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
