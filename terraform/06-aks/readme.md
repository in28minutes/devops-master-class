## Azure Kubernetes Cluster

### Create Resource Group & Storage Account

```
az group create -l westeurope -n RaviKubernetesResourceGroup
az storage account create -n ravik8sstorageacct -g RaviKubernetesResourceGroup -l westeurope --sku Standard_LRS
```

### Create Backend for Terraform State

```
az storage container create -n tfstate --account-name <<storage_account_name>> --account-key <<storage_account_key>>

terraform init -backend-config="storage_account_name=<<storage_account_name>>" -backend-config="container_name=tfstate" -backend-config="access_key=<<storage_account_key>>" -backend-config="key=codelab.microsoft.tfstate"
```

### Create Service Account For Your Subscription To Create Azure K8S Cluster

```
az login
az ad sp create-for-rbac --role="Contributor" --scopes="/subscriptions/<<azure_subscription_id>>"
export TF_VAR_client_id=<<service_account_appId>>
export TF_VAR_client_secret=<<service_account_password>>
```

### Create Public Key for SSH Access

```
ssh-keygen
ls /Users/rangakaranam/.ssh/id_rsa.pub
```

### Execute Terraform Commands

```
terraform apply
```

### Set Up kubectl 

```
terraform output kube_config>~/.kube/config
```

### Launch up 

```
kubectl proxy
open 'http://localhost:8001/api/v1/namespaces/kube-system/services/kubernetes-dashboard/proxy/#!/overview?namespace=default'
```