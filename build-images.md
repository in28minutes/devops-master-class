## Use Images supporting multiple architectures - linux/amd64,linux/arm64

```
FROM maven:3.8.2-jdk-8-slim AS build
```

## Execute buildx to create multi platform builds

```
docker buildx build \
--platform linux/amd64,linux/arm64 \
-t in28min/hello-world-python:0.0.1.RELEASE \
--push \
.

docker buildx build \
--platform linux/amd64,linux/arm64 \
-t in28min/hello-world-nodejs:0.0.1.RELEASE \
--push \
.

docker buildx build \
--platform linux/amd64,linux/arm64 \
-t in28min/hello-world-java:0.0.1.RELEASE \
--push \
.

# NOT EXECUTED
docker buildx build \
--platform linux/amd64,linux/arm64 \
-t in28min/currency-exchange:0.0.1-RELEASE \
--push \
.

# NOT EXECUTED
docker buildx build \
--platform linux/amd64,linux/arm64 \
-t in28min/currency-conversion:0.0.1-RELEASE \
--push \
.
```