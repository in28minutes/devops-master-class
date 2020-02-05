variable client_id {}
variable client_secret {}

variable environment {
    default = "dev"
}

variable location {
    default = "westeurope"
}

variable node_count {
  default = 3
}

variable ssh_public_key {
  default = "/Users/rangakaranam/.ssh/id_rsa.pub"
}

variable dns_prefix {
  default = "k8stest"
}

variable cluster_name {
  default = "k8stest"
}

variable resource_group {
  default = "kubernetes"
}