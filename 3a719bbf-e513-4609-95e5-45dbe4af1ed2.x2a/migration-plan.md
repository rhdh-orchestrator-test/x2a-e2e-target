# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated timeline for this migration is 3-4 weeks, with moderate complexity due to the security configurations and multi-site SSL setup.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled subdomains, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening with fail2ban and UFW

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks - will be replaced by Ansible Galaxy requirements.yml
- `Policyfile.rb`: Chef policy definition - will be replaced by Ansible playbook structure
- `Vagrantfile`: VM configuration for development - can be adapted for Ansible testing
- `solo.json`: Chef node attributes - will be converted to Ansible group_vars and host_vars
- `solo.rb`: Chef configuration - will be replaced by ansible.cfg
- `vagrant-provision.sh`: Provisioning script - will be replaced by Ansible provisioning

### Target Details

Based on the source configuration files:

- **Operating System**: Supports Ubuntu 18.04+ and CentOS 7+, with Fedora 42 used in Vagrant development environment
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or direct package installation
- **memcached (~> 6.0)**: Replace with Ansible memcached role or direct package installation
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or direct package installation
- **ssl_certificate (~> 2.1)**: Replace with Ansible certificate management modules (openssl_*)

### Security Considerations

- **SSL Certificate Management**: Migration must preserve self-signed certificate generation for development environments
- **Firewall Configuration**: UFW rules must be migrated to equivalent Ansible UFW module tasks
- **fail2ban Setup**: Configuration must be preserved in Ansible tasks
- **SSH Hardening**: SSH configuration hardening must be maintained
- **Redis Authentication**: Redis password must be securely managed in Ansible Vault
- **PostgreSQL Authentication**: Database credentials must be securely managed in Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of multiple site configurations with SSL needs careful translation to Ansible templates
- **Security Hardening**: Comprehensive security measures need to be maintained across the migration
- **Service Dependencies**: Ensuring proper ordering of service installations and configurations
- **PostgreSQL User/DB Creation**: Ensuring idempotent database operations in Ansible

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for web services)
   - Create base Nginx role
   - Implement SSL certificate generation
   - Configure multi-site setup
   - Implement security hardening

2. **cache** (low complexity, standalone services)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, application deployment)
   - Implement PostgreSQL setup
   - Configure Python environment
   - Deploy application code
   - Set up systemd service

### Assumptions

1. The current Chef setup is functional and represents the desired end state
2. Self-signed certificates are acceptable for development (production would likely use Let's Encrypt or other CA)
3. The hardcoded Redis password and PostgreSQL credentials will be moved to Ansible Vault
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git is accessible and contains the expected code
5. The target environment will continue to be Linux-based (Ubuntu/CentOS/Fedora)
6. No changes to the application architecture are required during migration

## Implementation Details

### Ansible Structure

```
ansible/
├── ansible.cfg
├── inventory/
│   ├── group_vars/
│   │   ├── all.yml
│   │   └── web_servers.yml
│   └── hosts
├── roles/
│   ├── nginx_multisite/
│   │   ├── defaults/
│   │   ├── files/
│   │   ├── handlers/
│   │   ├── tasks/
│   │   ├── templates/
│   │   └── vars/
│   ├── cache_services/
│   │   ├── defaults/
│   │   ├── handlers/
│   │   ├── tasks/
│   │   └── templates/
│   └── fastapi_app/
│       ├── defaults/
│       ├── handlers/
│       ├── tasks/
│       └── templates/
├── playbooks/
│   ├── site.yml
│   ├── nginx.yml
│   ├── cache.yml
│   └── fastapi.yml
└── requirements.yml
```

### Vault Strategy

Create an Ansible Vault file to store sensitive information:

```
ansible/
└── inventory/
    └── group_vars/
        └── all/
            └── vault.yml  # Encrypted file containing passwords and secrets
```

### Testing Strategy

1. Develop Vagrant-based testing environment similar to the existing one
2. Create test playbooks to verify each role independently
3. Implement integration tests to verify the complete stack
4. Compare outputs and configurations with the original Chef-managed environment

### Documentation Requirements

1. README with setup instructions
2. Role-specific documentation
3. Variable reference
4. Deployment guide
5. Migration notes for future reference