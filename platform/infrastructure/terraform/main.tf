# IRIS Platform Infrastructure
# Terraform configuration for cloud deployment

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.20"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.10"
    }
  }
}

# Variables
variable "cluster_name" {
  description = "Name of the EKS cluster"
  type        = string
  default     = "iris-platform"
}

variable "cluster_version" {
  description = "Kubernetes version"
  type        = string
  default     = "1.27"
}

variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "domain_name" {
  description = "Domain name for the platform"
  type        = string
  default     = "iris-platform.example.com"
}

# Data sources
data "aws_availability_zones" "available" {
  filter {
    name   = "opt-in-status"
    values = ["opt-in-not-required"]
  }
}

data "aws_caller_identity" "current" {}

# VPC
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = "${var.cluster_name}-vpc"
  cidr = "10.0.0.0/16"

  azs             = slice(data.aws_availability_zones.available.names, 0, 3)
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway   = true
  single_nat_gateway   = var.environment == "dev"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    "kubernetes.io/cluster/${var.cluster_name}" = "shared"
    Environment = var.environment
  }

  public_subnet_tags = {
    "kubernetes.io/cluster/${var.cluster_name}" = "shared"
    "kubernetes.io/role/elb"                    = "1"
  }

  private_subnet_tags = {
    "kubernetes.io/cluster/${var.cluster_name}" = "shared"
    "kubernetes.io/role/internal-elb"           = "1"
  }
}

# EKS Cluster
module "eks" {
  source = "terraform-aws-modules/eks/aws"

  cluster_name    = var.cluster_name
  cluster_version = var.cluster_version

  vpc_id                         = module.vpc.vpc_id
  subnet_ids                     = module.vpc.private_subnets
  cluster_endpoint_public_access = true

  eks_managed_node_groups = {
    main = {
      name = "main"

      instance_types = [var.environment == "prod" ? "m5.large" : "t3.medium"]

      min_size     = var.environment == "prod" ? 3 : 1
      max_size     = var.environment == "prod" ? 10 : 5
      desired_size = var.environment == "prod" ? 3 : 2

      pre_bootstrap_user_data = <<-EOT
        echo 'net.ipv4.ip_forward = 1' >> /etc/sysctl.conf
        sysctl -p
      EOT

      vpc_security_group_ids = [aws_security_group.additional.id]
    }

    gpu = {
      name = "gpu-nodes"

      instance_types = ["g4dn.xlarge"]
      ami_type       = "AL2_x86_64_GPU"

      min_size     = 0
      max_size     = 3
      desired_size = var.environment == "prod" ? 1 : 0

      labels = {
        "iris.io/node-type" = "gpu"
      }

      taints = [
        {
          key    = "nvidia.com/gpu"
          value  = "true"
          effect = "NO_SCHEDULE"
        }
      ]
    }
  }

  # aws-auth configmap
  manage_aws_auth_configmap = true

  aws_auth_roles = [
    {
      rolearn  = aws_iam_role.eks_admin.arn
      username = "eks-admin"
      groups   = ["system:masters"]
    },
  ]

  tags = {
    Environment = var.environment
  }
}

# Additional security group for EKS nodes
resource "aws_security_group" "additional" {
  name_prefix = "${var.cluster_name}-additional"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port = 22
    to_port   = 22
    protocol  = "tcp"
    cidr_blocks = [
      "10.0.0.0/8",
      "172.16.0.0/12",
      "192.168.0.0/16",
    ]
  }

  tags = {
    Name = "${var.cluster_name}-additional"
  }
}

# IAM role for EKS administration
resource "aws_iam_role" "eks_admin" {
  name = "${var.cluster_name}-eks-admin"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
      }
    ]
  })
}

# RDS for PostgreSQL
resource "aws_db_subnet_group" "iris" {
  name       = "${var.cluster_name}-db-subnet-group"
  subnet_ids = module.vpc.private_subnets

  tags = {
    Name = "${var.cluster_name} DB subnet group"
  }
}

resource "aws_security_group" "rds" {
  name_prefix = "${var.cluster_name}-rds"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [module.vpc.vpc_cidr_block]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.cluster_name}-rds"
  }
}

resource "aws_db_instance" "iris" {
  identifier = "${var.cluster_name}-postgres"

  engine         = "postgres"
  engine_version = "15.4"
  instance_class = var.environment == "prod" ? "db.r6g.large" : "db.t3.micro"

  allocated_storage     = var.environment == "prod" ? 100 : 20
  max_allocated_storage = var.environment == "prod" ? 1000 : 100

  storage_encrypted = true
  kms_key_id       = aws_kms_key.iris.arn

  db_name  = "iris_platform"
  username = "iris_admin"
  password = random_password.db_password.result

  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.iris.name

  backup_retention_period = var.environment == "prod" ? 30 : 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"

  skip_final_snapshot       = var.environment != "prod"
  final_snapshot_identifier = var.environment == "prod" ? "${var.cluster_name}-final-snapshot" : null

  tags = {
    Name        = "${var.cluster_name}-postgres"
    Environment = var.environment
  }
}

# ElastiCache for Redis
resource "aws_elasticache_subnet_group" "iris" {
  name       = "${var.cluster_name}-cache-subnet"
  subnet_ids = module.vpc.private_subnets
}

resource "aws_security_group" "redis" {
  name_prefix = "${var.cluster_name}-redis"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    cidr_blocks = [module.vpc.vpc_cidr_block]
  }

  tags = {
    Name = "${var.cluster_name}-redis"
  }
}

resource "aws_elasticache_replication_group" "iris" {
  replication_group_id         = "${var.cluster_name}-redis"
  description                  = "Redis cluster for IRIS platform"

  node_type                    = var.environment == "prod" ? "cache.r6g.large" : "cache.t3.micro"
  port                         = 6379
  parameter_group_name         = "default.redis7"

  num_cache_clusters           = var.environment == "prod" ? 3 : 1
  automatic_failover_enabled   = var.environment == "prod"
  multi_az_enabled            = var.environment == "prod"

  subnet_group_name           = aws_elasticache_subnet_group.iris.name
  security_group_ids          = [aws_security_group.redis.id]

  at_rest_encryption_enabled  = true
  transit_encryption_enabled  = true
  auth_token                  = random_password.redis_password.result

  snapshot_retention_limit    = var.environment == "prod" ? 7 : 1
  snapshot_window             = "03:00-05:00"

  tags = {
    Name        = "${var.cluster_name}-redis"
    Environment = var.environment
  }
}

# S3 bucket for object storage
resource "aws_s3_bucket" "iris" {
  bucket = "${var.cluster_name}-${var.environment}-storage"

  tags = {
    Name        = "${var.cluster_name}-storage"
    Environment = var.environment
  }
}

resource "aws_s3_bucket_versioning" "iris" {
  bucket = aws_s3_bucket.iris.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_encryption" "iris" {
  bucket = aws_s3_bucket.iris.id

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        kms_master_key_id = aws_kms_key.iris.arn
        sse_algorithm     = "aws:kms"
      }
    }
  }
}

resource "aws_s3_bucket_public_access_block" "iris" {
  bucket = aws_s3_bucket.iris.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# KMS key for encryption
resource "aws_kms_key" "iris" {
  description             = "KMS key for IRIS platform"
  deletion_window_in_days = 7

  tags = {
    Name        = "${var.cluster_name}-kms"
    Environment = var.environment
  }
}

resource "aws_kms_alias" "iris" {
  name          = "alias/${var.cluster_name}-${var.environment}"
  target_key_id = aws_kms_key.iris.key_id
}

# Random passwords
resource "random_password" "db_password" {
  length  = 32
  special = true
}

resource "random_password" "redis_password" {
  length  = 32
  special = false
}

# Secrets Manager for storing sensitive data
resource "aws_secretsmanager_secret" "iris" {
  name                    = "${var.cluster_name}-${var.environment}-secrets"
  description             = "Secrets for IRIS platform"
  kms_key_id              = aws_kms_key.iris.arn
  recovery_window_in_days = 0 # For dev/staging
}

resource "aws_secretsmanager_secret_version" "iris" {
  secret_id = aws_secretsmanager_secret.iris.id
  secret_string = jsonencode({
    database_password = random_password.db_password.result
    redis_password    = random_password.redis_password.result
    jwt_secret        = random_password.jwt_secret.result
    jwt_refresh_secret = random_password.jwt_refresh_secret.result
  })
}

resource "random_password" "jwt_secret" {
  length  = 64
  special = false
}

resource "random_password" "jwt_refresh_secret" {
  length  = 64
  special = false
}

# OpenSearch (ElasticSearch alternative)
resource "aws_opensearch_domain" "iris" {
  count           = var.environment == "prod" ? 1 : 0
  domain_name     = "${var.cluster_name}-search"
  engine_version  = "OpenSearch_2.5"

  cluster_config {
    instance_type  = "t3.small.search"
    instance_count = 3
  }

  ebs_options {
    ebs_enabled = true
    volume_type = "gp3"
    volume_size = 20
  }

  vpc_options {
    subnet_ids         = slice(module.vpc.private_subnets, 0, 2)
    security_group_ids = [aws_security_group.opensearch[0].id]
  }

  encrypt_at_rest {
    enabled    = true
    kms_key_id = aws_kms_key.iris.arn
  }

  node_to_node_encryption {
    enabled = true
  }

  domain_endpoint_options {
    enforce_https       = true
    tls_security_policy = "Policy-Min-TLS-1-2-2019-07"
  }

  tags = {
    Name        = "${var.cluster_name}-search"
    Environment = var.environment
  }
}

resource "aws_security_group" "opensearch" {
  count       = var.environment == "prod" ? 1 : 0
  name_prefix = "${var.cluster_name}-opensearch"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [module.vpc.vpc_cidr_block]
  }

  tags = {
    Name = "${var.cluster_name}-opensearch"
  }
}

# Outputs
output "cluster_endpoint" {
  description = "Endpoint for EKS control plane"
  value       = module.eks.cluster_endpoint
}

output "cluster_name" {
  description = "EKS cluster name"
  value       = module.eks.cluster_name
}

output "database_endpoint" {
  description = "RDS instance endpoint"
  value       = aws_db_instance.iris.endpoint
  sensitive   = true
}

output "redis_endpoint" {
  description = "ElastiCache Redis endpoint"
  value       = aws_elasticache_replication_group.iris.primary_endpoint_address
  sensitive   = true
}

output "s3_bucket" {
  description = "S3 bucket name"
  value       = aws_s3_bucket.iris.bucket
}

output "secrets_manager_secret_arn" {
  description = "Secrets Manager secret ARN"
  value       = aws_secretsmanager_secret.iris.arn
}

output "opensearch_endpoint" {
  description = "OpenSearch domain endpoint"
  value       = var.environment == "prod" ? aws_opensearch_domain.iris[0].endpoint : null
}