# Currency Exchange Micro Service - H2

Run com.in28minutes.microservices.currencyconversionservice.CurrencyConversionServiceApplicationH2 as a Java Application.

## Resources

- http://localhost:8000/currency-exchange/from/USD/to/INR

```json
{
  "id": 10001,
  "from": "USD",
  "to": "INR",
  "conversionMultiple": 65.00,
  "environmentInfo": "NA"
}
```

## H2 Console

- http://localhost:8000/h2-console
- Use `jdbc:h2:mem:testdb` as JDBC URL


## Notes

## Tables Created
```
create table exchange_value 
(
	id bigint not null, 
	conversion_multiple decimal(19,2), 
	currency_from varchar(255), 
	currency_to varchar(255), 
	primary key (id)
)
```

## Containerization

### Troubleshooting

- Problem - Caused by: com.spotify.docker.client.shaded.javax.ws.rs.ProcessingException: java.io.IOException: No such file or directory
- Solution - Check if docker is up and running!
- Problem - Error creating the Docker image on MacOS - java.io.IOException: Cannot run program “docker-credential-osxkeychain”: error=2, No such file or directory
- Solution - https://medium.com/@dakshika/error-creating-the-docker-image-on-macos-wso2-enterprise-integrator-tooling-dfb5b537b44e

### Creating Container

- mvn package

### Running Container

#### Basic
```
docker container run --publish 8000:8000 in28min/currency-exchange:0.0.1-SNAPSHOT
```


## Auto Scaling

### Cluster Auto Scaling

```
gcloud container clusters create example-cluster \
--zone us-central1-a \
--node-locations us-central1-a,us-central1-b,us-central1-f \
--num-nodes 2 --enable-autoscaling --min-nodes 1 --max-nodes 4
```
### Vertical Pod Auto Scaling
- Available in version 1.14.7-gke.10 or higher and in 1.15.4-gke.15 or higher

#### Enable on Cluster

```
gcloud container clusters create [CLUSTER_NAME] --enable-vertical-pod-autoscaling --cluster-version=1.14.7
gcloud container clusters update [CLUSTER-NAME] --enable-vertical-pod-autoscaling
```

#### Configure VPA

```
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: currency-exchange-vpa
spec:
  targetRef:
    apiVersion: "apps/v1"
    kind:       Deployment
    name:       currency-exchange
  updatePolicy:
    updateMode: "Off"
```

#### Get Recommendations

```
kubectl get vpa currency-exchange-vpa --output yaml
```

### Horizontal Pod Auto Scaling

```
kubectl autoscale deployment currency-exchange-service --max=3 --min=1 --cpu-percent=50
```