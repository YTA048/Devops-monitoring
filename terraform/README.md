# Terraform — DevOps Monitoring Platform

Provisionne sur AWS l'infrastructure d'hébergement de la stack monitoring.

## Ressources créées

- 1 VPC (10.0.0.0/16) + Internet Gateway + Route Table publique
- 1 Subnet public (10.0.1.0/24)
- 1 Security Group (SSH + ports observabilité)
- 1 EC2 t3.micro (Amazon Linux 2023, AMI résolue dynamiquement)
- User-data installant Docker + Docker Compose

## Prérequis

- Terraform >= 1.5
- Compte AWS + credentials configurés (`aws configure` ou variables d'env)
- (Optionnel) Une key pair AWS si vous voulez SSH

## Utilisation

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
# éditer terraform.tfvars avec vos valeurs

terraform init
terraform plan
terraform apply
```

À la fin, les URLs Grafana / Prometheus / Kibana / Jaeger sont affichées en outputs.

## Destruction

```bash
terraform destroy
```

## Sécurité

Par défaut `ssh_cidr = "0.0.0.0/0"` ouvre SSH au monde — **à restreindre** à votre IP en production (`X.X.X.X/32`).
