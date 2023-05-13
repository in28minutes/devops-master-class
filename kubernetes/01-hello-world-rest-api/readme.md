# Hello World Rest API

### Running the Application

Run com.in28minutes.rest.webservices.restfulwebservices.RestfulWebServicesApplication as a Java Application.

- http://localhost:8080/hello-world

```txt
Hello World V1 abcde
```

- http://localhost:8080/hello-world-bean

```json
{"message":"Hello World"}
```

- http://localhost:8080/hello-world/path-variable/in28minutes

```json
{"message":"Hello World, in28minutes"}
```

# You will see this fail with GITHUB issue : https://github.com/in28minutes/devops-master-class/issues/28
# To over come this issue, you need to build the JAR file.
# To build the JAR file : 
mvn clean install