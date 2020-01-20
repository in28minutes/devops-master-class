# Master Devops - Docker, Kubernetes, Terraform and Azure Devops

## Learn Devops with Docker, Kubernetes, Terraform, Ansible, Jenkins and Azure Devops

## 

## Next Steps

## Todo
- COURSE - ADD ALL THE COMMANDS
- Using Dockerfile
- Understanding Docker Image Layers, Caching and Dockerfile
docker-compose up
docker-compose up -d
docker-compose scale currency-conversion-service=2
docker-compose logs
docker-compose logs -f
```
docker inspect in28min/hello-world-rest-api:dockerfile1
docker history in28min/hello-world-rest-api:dockerfile1
docker build -t in28min/hello-world-rest-api:dockerfile1 .
```
- Caching of Docker Images - Improve Caching and Being able to run it anywhere!
- Course Promotion Emails/Posts
  - 2 Emails on Udemy
  - 2 Emails to Email List
- Create YouTube Course Preview Video
  - Add YouTube Course Preview Video as End Video for all videos
  - Make it the YouTube Default Video
- Release atleast 20 small videos - one a day on Youtube
- Do atleast 3 Youtube live sessions
- After a Month
  - UFB and Packt

## Diagrams

```
graph architecture {

node[style=filled,color="#59C8DE"]
//node [style=filled,color="#D14D28", fontcolor=white];
rankdir = TB
node[shape=record, width=2]
Level1[shape=record, width=7.0, style=filled,color="#D14D28", fontcolor=white]
edge [width=0]
graph [pad=".75", ranksep="0.05", nodesep="0.25"];
Block1,Block2,Block3[height=2]

Block1 -- Level1 [style=invis]
Block2 -- Level1 [style=invis]
Block3 -- Level1 [style=invis]

Level1[label=<Docker>]
Block1[label=<Standaridized <BR/> Application Packaging <BR/><BR/> <FONT POINT-SIZE="10">Same packaging for <BR/>all types of applications <BR/><BR/> - Java, Python or JS</FONT>>]
Block2[label=<Multi  <BR/> Platform Support <BR/><BR/> <FONT POINT-SIZE="10">Local Machine <BR/> Data Center <BR/> Cloud - AWS, Azure and GCP</FONT>>]
Block3[label=<Isolation <BR/><BR/><BR/><FONT POINT-SIZE="10"> Containers have isolation <BR/> from one another</FONT>>]

}
```