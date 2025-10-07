# IRIS Research Platform - Standalone Architecture

A comprehensive research platform built on the IRIS protocol for consciousness and AI research.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        IRIS Platform                           │
├─────────────────────────────────────────────────────────────────┤
│                     Frontend Layer                             │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐   │
│  │   Web UI        │ │   Mobile App    │ │   CLI Tools     │   │
│  │   (React)       │ │   (PWA)         │ │   (Python)      │   │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘   │
├─────────────────────────────────────────────────────────────────┤
│                     API Gateway                                │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  Authentication │ Rate Limiting │ Load Balancing │ Routing │ │
│  └─────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│                   Microservices Layer                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌───────────┐ │
│  │   User      │ │  Research   │ │    Data     │ │Integration│ │
│  │  Service    │ │   Engine    │ │  Platform   │ │    Hub    │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └───────────┘ │
├─────────────────────────────────────────────────────────────────┤
│                    Data Layer                                  │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌───────────┐ │
│  │PostgreSQL   │ │   Redis     │ │   MinIO     │ │  Search   │ │
│  │(Metadata)   │ │  (Cache)    │ │ (Objects)   │ │(OpenSearch)│ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └───────────┘ │
├─────────────────────────────────────────────────────────────────┤
│                Infrastructure Layer                            │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │     Kubernetes / Docker Swarm / Docker Compose             │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Key Features

### Multi-User Research Teams
- Organization-based multi-tenancy
- Role-based access control (Admin, Researcher, Collaborator, Viewer)
- Team workspaces with shared resources
- User management with SSO integration

### Research Engine
- Containerized S1-S8 protocol pipeline
- Multi-model orchestration (Claude, GPT, Gemini, etc.)
- Real-time session monitoring
- Automated analysis and convergence detection

### Data Platform
- Version-controlled research data
- Secure data sharing between teams
- Export to standard formats (JSON, CSV, markdown)
- Compliance with research data standards

### Web Interface
- Progressive Web App (works offline)
- Real-time collaboration features
- Visual session monitoring and analysis
- Mobile-responsive design

### API Access
- RESTful API for power users
- GraphQL for complex queries
- WebSocket for real-time updates
- Comprehensive SDK in Python/JavaScript

### Deployment Options
- Cloud-native (AWS, GCP, Azure)
- Self-hosted (on-premise)
- Hybrid deployments
- Development docker-compose setup

## Directory Structure

```
platform/
├── README.md                     # This file
├── docker-compose.yml           # Development environment
├── kubernetes/                  # K8s manifests
├── services/                    # Microservices
│   ├── api-gateway/            # Kong/Traefik API gateway
│   ├── user-service/           # Authentication & user management
│   ├── research-engine/        # IRIS protocol engine
│   ├── data-platform/          # Data management service
│   ├── integration-hub/        # External AI integrations
│   └── notification-service/   # Email/Slack notifications
├── frontend/                   # Web application
│   ├── web-ui/                # React web interface
│   ├── mobile/               # PWA mobile app
│   └── cli/                  # Command-line tools
├── infrastructure/            # Infrastructure as code
│   ├── terraform/            # Cloud provisioning
│   ├── ansible/             # Configuration management
│   └── monitoring/          # Observability stack
└── docs/                    # Platform documentation
```

## Quick Start

### Development Environment
```bash
git clone <repository>
cd iris-gate/platform
docker-compose up -d
```

### Production Deployment
```bash
# Kubernetes
kubectl apply -f kubernetes/

# Or Docker Swarm
docker stack deploy -c docker-stack.yml iris-platform
```

## Business Model Options

1. **Open Source Core + Enterprise Features**
2. **SaaS with usage-based pricing**
3. **On-premise licensing**
4. **Research institution partnerships**

See [Business Model Documentation](docs/business-model.md) for details.