# Kubernetes

## Projects
- Hello World REST API
- 2 Microservices - Currency Exchange and Currency Conversion

## Steps
- Step 01 - Getting Started with Docker, Kubernetes and Google Kubernetes Engine
- Step 02 - Creating Google Cloud Account
- Step 03 - Creating Kubernetes Cluster with Google Kubernete Engine (GKE)
- Step 04 - Review Kubernetes Cluster and Learn Few Fun Facts about Kubernetes
- Step 05 - Deploy Your First Spring Boot Application to Kubernetes Cluster
- Step 06 - Quick Look at Kubernetes Concepts - Pods, Replica Sets and Deployment
- Step 07 - Understanding Pods in Kubernetes
- Step 08 - Understanding ReplicaSets in Kubernetes
- Step 09 - Understanding Deployment in Kubernetes
- Step 10 - Quick Review of Kubernetes Concepts - Pods, Replica Sets and Deployment
- Step 11 - Understanding Services in Kubernetes
- Step 12 - Quick Review of GKE on Google Cloud Console 
- Step 13 - Understanding Kubernetes Architecture - Master Node and Nodes
- Step 14 - Understand Google Cloud Regions and Zones
- Step 15 - Installing GCloud
- Step 16 - Installing Kubectl 
- Step 17 - Understand Kubernetes Rollouts
- Step 18 - Generate Kubernetes YAML Configuration for Deployment and Service
- Step 19 - Understand and Improve Kubernetes YAML Configuration
- Step 20 - Using Kubernetes YAML Configuration to Create Resources
- Step 21 - Understanding Kubernetes YAML Configuration - Labels and Selectors
- Step 22 - Quick Fix to reduce release downtime with minReadySeconds
- Step 23 - Understanding Replica Sets in Depth - Using Kubernetes YAML Config
- Step 24 - Configure Multiple Kubernetes Deployments with One Service
- Step 25 - Playing with Kubernetes Commands - Top Node and Pod
- Step 26 - Delete Hello World Deployments
- Step 27 - Quick Introduction to Microservices - CE and CC
- Step 28 - Deploy Microservices to Kubernetes
- Step 29 - Understand Environment Variables created by Kubernetes for Services
- Step 30 - Microservices and Kubernetes Service Discovery - Part 1
- Step 31 - Microservices and Kubernetes Service Discovery - Part 2 DNS
- Step 32 - Microservices Centralized Configuration with Kubernetes ConfigMaps
- Step 33 - Simplify Microservices with Kubernetes Ingress - Part 1
- Step 34 - Simplify Microservices with Kubernetes Ingress - Part 2
- Step 35 - Delete Kubernetes Clusters


## Commands

```
docker run -p 8080:8080 in28min/hello-world-rest-api:0.0.1.RELEASE

kubectl create deployment hello-world-rest-api --image=in28min/hello-world-rest-api:0.0.1.RELEASE
kubectl expose deployment hello-world-rest-api --type=LoadBalancer --port=8080
kubectl scale deployment hello-world-rest-api --replicas=3
kubectl delete pod hello-world-rest-api-58ff5dd898-62l9d
kubectl autoscale deployment hello-world-rest-api --max=10 --cpu-percent=70
kubectl edit deployment hello-world-rest-api #minReadySeconds: 15
kubectl set image deployment hello-world-rest-api hello-world-rest-api=in28min/hello-world-rest-api:0.0.2.RELEASE

gcloud container clusters get-credentials in28minutes-cluster --zone us-central1-a --project solid-course-258105
kubectl create deployment hello-world-rest-api --image=in28min/hello-world-rest-api:0.0.1.RELEASE
kubectl expose deployment hello-world-rest-api --type=LoadBalancer --port=8080
kubectl set image deployment hello-world-rest-api hello-world-rest-api=DUMMY_IMAGE:TEST
kubectl get events --sort-by=.metadata.creationTimestamp
kubectl set image deployment hello-world-rest-api hello-world-rest-api=in28min/hello-world-rest-api:0.0.2.RELEASE
kubectl get events --sort-by=.metadata.creationTimestamp
kubectl get componentstatuses
kubectl get pods --all-namespaces

kubectl get events
kubectl get pods
kubectl get replicaset
kubectl get deployment
kubectl get service

kubectl get pods -o wide

kubectl explain pods
kubectl get pods -o wide

kubectl describe pod hello-world-rest-api-58ff5dd898-9trh2

kubectl get replicasets
kubectl get replicaset

kubectl scale deployment hello-world-rest-api --replicas=3
kubectl get pods
kubectl get replicaset
kubectl get events
kubectl get events --sort-by=.metadata.creationTimestamp

kubectl get rs
kubectl get rs -o wide
kubectl set image deployment hello-world-rest-api hello-world-rest-api=DUMMY_IMAGE:TEST
kubectl get rs -o wide
kubectl get pods
kubectl describe pod hello-world-rest-api-85995ddd5c-msjsm
kubectl get events --sort-by=.metadata.creationTimestamp

kubectl set image deployment hello-world-rest-api hello-world-rest-api=in28min/hello-world-rest-api:0.0.2.RELEASE
kubectl get events --sort-by=.metadata.creationTimestamp
kubectl get pods -o wide
kubectl delete pod hello-world-rest-api-67c79fd44f-n6c7l
kubectl get pods -o wide
kubectl delete pod hello-world-rest-api-67c79fd44f-8bhdt

kubectl get componentstatuses
kubectl get pods --all-namespaces

gcloud auth login
kubectl version
gcloud container clusters get-credentials in28minutes-cluster --zone us-central1-a --project solid-course-258105

kubectl rollout history deployment hello-world-rest-api
kubectl set image deployment hello-world-rest-api hello-world-rest-api=in28min/hello-world-rest-api:0.0.3.RELEASE --record=true
kubectl rollout undo deployment hello-world-rest-api --to-revision=1

kubectl logs hello-world-rest-api-58ff5dd898-6ctr2
kubectl logs -f hello-world-rest-api-58ff5dd898-6ctr2

kubectl get deployment hello-world-rest-api -o yaml
kubectl get deployment hello-world-rest-api -o yaml > deployment.yaml
kubectl get service hello-world-rest-api -o yaml > service.yaml
kubectl apply -f deployment.yaml
kubectl get all -o wide
kubectl delete all -l app=hello-world-rest-api

kubectl get svc --watch
kubectl diff -f deployment.yaml
kubectl delete deployment hello-world-rest-api
kubectl get all -o wide
kubectl delete replicaset.apps/hello-world-rest-api-797dd4b5dc

kubectl get pods --all-namespaces
kubectl get pods --all-namespaces -l app=hello-world-rest-api
kubectl get services --all-namespaces
kubectl get services --all-namespaces --sort-by=.spec.type
kubectl get services --all-namespaces --sort-by=.metadata.name
kubectl cluster-info
kubectl cluster-info dump
kubectl top node
kubectl top pod
kubectl get services
kubectl get svc
kubectl get ev
kubectl get rs
kubectl get ns
kubectl get nodes
kubectl get no
kubectl get pods
kubectl get po

kubectl delete all -l app=hello-world-rest-api
kubectl get all

kubectl apply -f deployment.yaml 
kubectl apply -f ../currency-conversion/deployment.yaml 
```
