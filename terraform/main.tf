###############################################################################
# DevOps Monitoring Platform - Infrastructure AWS
#
# Provisionne :
#   - Un VPC dédié avec un Internet Gateway et une route publique
#   - Un Subnet public dans une AZ
#   - Un Security Group autorisant SSH + ports d'observabilité
#   - Une EC2 t3.micro (Amazon Linux 2023 - AMI dynamique)
#   - User-data installant Docker + Docker Compose et clonant le repo
###############################################################################

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

###############################################################################
# Variables
###############################################################################

variable "aws_region" {
  description = "Région AWS du déploiement"
  type        = string
  default     = "eu-west-3"
}

variable "project_name" {
  description = "Nom du projet (utilisé pour le tagging)"
  type        = string
  default     = "devops-monitoring"
}

variable "instance_type" {
  description = "Type d'instance EC2"
  type        = string
  default     = "t3.micro"
}

variable "ssh_cidr" {
  description = "CIDR autorisé pour SSH (à restreindre en prod)"
  type        = string
  default     = "0.0.0.0/0"
}

variable "key_name" {
  description = "Nom de la key pair AWS existante pour SSH"
  type        = string
  default     = ""
}

###############################################################################
# Data sources
###############################################################################

# AMI Amazon Linux 2023 la plus récente (AMI dynamique, pas hardcodée)
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-2023.*-x86_64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# Première AZ disponible dans la région
data "aws_availability_zones" "available" {
  state = "available"
}

###############################################################################
# Networking : VPC + Subnet + IGW + Route Table
###############################################################################

resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name    = "${var.project_name}-vpc"
    Project = var.project_name
  }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name    = "${var.project_name}-igw"
    Project = var.project_name
  }
}

resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = data.aws_availability_zones.available.names[0]
  map_public_ip_on_launch = true

  tags = {
    Name    = "${var.project_name}-public-subnet"
    Project = var.project_name
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name    = "${var.project_name}-public-rt"
    Project = var.project_name
  }
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

###############################################################################
# Security Group
###############################################################################

resource "aws_security_group" "monitoring" {
  name        = "${var.project_name}-sg"
  description = "Allow SSH and observability stack ports"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.ssh_cidr]
  }

  ingress {
    description = "FastAPI backend"
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "React frontend"
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Grafana"
    from_port   = 3001
    to_port     = 3001
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Prometheus"
    from_port   = 9090
    to_port     = 9090
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Jaeger UI"
    from_port   = 16686
    to_port     = 16686
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Kibana"
    from_port   = 5601
    to_port     = 5601
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "AlertManager"
    from_port   = 9093
    to_port     = 9093
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "All outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name    = "${var.project_name}-sg"
    Project = var.project_name
  }
}

###############################################################################
# EC2 instance
###############################################################################

resource "aws_instance" "monitoring" {
  ami                         = data.aws_ami.amazon_linux.id
  instance_type               = var.instance_type
  subnet_id                   = aws_subnet.public.id
  vpc_security_group_ids      = [aws_security_group.monitoring.id]
  associate_public_ip_address = true
  key_name                    = var.key_name != "" ? var.key_name : null

  user_data = <<-EOF
    #!/bin/bash
    set -euxo pipefail

    # Update system
    dnf update -y

    # Install Docker
    dnf install -y docker git
    systemctl enable --now docker
    usermod -aG docker ec2-user

    # Install Docker Compose v2 plugin
    DOCKER_CONFIG=/usr/local/lib/docker
    mkdir -p $DOCKER_CONFIG/cli-plugins
    curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 \
      -o $DOCKER_CONFIG/cli-plugins/docker-compose
    chmod +x $DOCKER_CONFIG/cli-plugins/docker-compose

    # Increase vm.max_map_count for Elasticsearch
    echo "vm.max_map_count=262144" >> /etc/sysctl.conf
    sysctl -p

    # Clone the project (URL à ajuster)
    cd /home/ec2-user
    # git clone https://github.com/<user>/devops-monitoring.git
    # cd devops-monitoring && docker compose up -d
  EOF

  root_block_device {
    volume_size           = 30
    volume_type           = "gp3"
    delete_on_termination = true
    encrypted             = true
  }

  tags = {
    Name    = "${var.project_name}-ec2"
    Project = var.project_name
    Role    = "monitoring-host"
  }
}

###############################################################################
# Outputs
###############################################################################

output "ec2_public_ip" {
  description = "IP publique de l'instance"
  value       = aws_instance.monitoring.public_ip
}

output "ec2_public_dns" {
  description = "DNS public de l'instance"
  value       = aws_instance.monitoring.public_dns
}

output "grafana_url" {
  value = "http://${aws_instance.monitoring.public_dns}:3001"
}

output "prometheus_url" {
  value = "http://${aws_instance.monitoring.public_dns}:9090"
}

output "kibana_url" {
  value = "http://${aws_instance.monitoring.public_dns}:5601"
}

output "jaeger_url" {
  value = "http://${aws_instance.monitoring.public_dns}:16686"
}
