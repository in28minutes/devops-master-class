# Azure DevOps

## Azure Marketplace

- Terraform 1 (https://marketplace.visualstudio.com/items?itemName=ms-devlabs.custom-terraform-tasks)
- Terraform 2 (https://marketplace.visualstudio.com/items?itemName=charleszipp.azure-pipelines-tasks-terraform)
- Aws (https://marketplace.visualstudio.com/items?itemName=AmazonWebServices.aws-vsts-tools)

## Azure Kubernetes Cluster

Pre-requisites
- Service Account
- SSH Public Key

### Create Service Account For Your Subscription To Create Azure K8S Cluster using Terraform

```
az login
az ad sp create-for-rbac --role="Contributor" --scopes="/subscriptions/<<azure_subscription_id>>"
```

### Create Public Key for SSH Access

```
ssh-keygen -m PEM -t rsa -b 4096 # PEM - Privacy Enhanced Mail - Certificate Format RSA- Encryption Algorithm
ls /Users/rangakaranam/.ssh/id_rsa.pub
```

### Get Cluster Credentials

az aks get-credentials --name <<MyManagedCluster>> --resource-group <<MyResourceGroup>>



# Backup - DO NOT USE

### Manually setting up from local machine

#### Create Service Account For Your Subscription To Create Azure K8S Cluster using Terraform

```
az login
az ad sp create-for-rbac --role="Contributor" --scopes="/subscriptions/<<azure_subscription_id>>"
export TF_VAR_client_id=<<service_account_appId>>
export TF_VAR_client_secret=<<service_account_password>>
```

#### Create Public Key for SSH Access

```
ssh-keygen -m PEM -t rsa -b 4096 # PEM - Privacy Enhanced Mail - Certificate Format RSA- Encryption Algorithm
ls /Users/rangakaranam/.ssh/id_rsa.pub
```

#### Create Resource Group, Storage Account and Storage Container

```
az group create -l westeurope -n In28minutesK8sResourceGroup
az storage account create -n In28minutesK8sStorageAccount -g In28minutesK8sResourceGroup -l westeurope --sku Standard_LRS
az storage container create -n devterraformstatestorage --account-name <<storage_account_name>> --account-key <<storage_account_key>>

```

#### Execute Terraform Commands

```
# comment backend
terraform init
terraform apply
# add backend
# terraform init with backend
terraform init -backend-config="storage_account_name=<<storage_account_name>>" -backend-config="container_name=<<storage_container_name>>" -backend-config="access_key=<<storage_account_key>>" -backend-config="key=<<k8s.environment.tfstate>>"

```


#### Set Up kubectl 

```
terraform output kube_config>~/.kube/config
```

#### Launch up 

```
kubectl proxy
open 'http://localhost:8001/api/v1/namespaces/kube-system/services/kubernetes-dashboard/proxy/#!/overview?namespace=default'
```