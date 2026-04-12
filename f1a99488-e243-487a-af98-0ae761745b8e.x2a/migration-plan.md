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

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `Policyfile.rb`: Chef policy file defining the run list and cookbook dependencies
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings
- `solo.json`: Node attributes and run list configuration for Chef Solo
- `Vagrantfile`: Defines a Fedora 42 VM for testing with port forwarding and networking
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (primary) with support for Ubuntu 18.04+ and CentOS 7+ based on cookbook metadata
- **Virtual Machine Technology**: Libvirt (specified in Vagrantfile)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or nginx_core module
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks
- **ssl_certificate (~> 2.1)**: Replace with Ansible openssl module for certificate generation

### Security Considerations

- **SSL Certificate Management**: Migration must handle self-signed certificate generation for multiple sites
- **Firewall Configuration**: UFW rules need to be migrated to equivalent Ansible ufw module tasks
- **fail2ban Configuration**: Configuration needs to be migrated to Ansible tasks
- **SSH Hardening**: SSH security settings (disable root login, password authentication) need to be preserved
- **Redis Authentication**: Redis password must be securely managed in Ansible Vault
- **PostgreSQL Authentication**: Database credentials must be securely managed in Ansible Vault

### Technical Challenges

- **Multi-site Configuration**: The dynamic generation of multiple Nginx site configurations needs careful handling in Ansible
- **SSL Certificate Generation**: Self-signed certificate generation for multiple domains needs to be properly implemented
- **Service Dependencies**: Ensuring proper ordering of service installations and configurations (e.g., PostgreSQL before FastAPI app)
- **Idempotency**: Ensuring database creation tasks are idempotent (current implementation uses "|| true" to handle errors)

### Migration Order

1. **nginx-multisite cookbook** (moderate complexity, foundation for other services)
   - Base Nginx installation and configuration
   - SSL certificate generation
   - Multi-site configuration
   - Security hardening (fail2ban, UFW)

2. **cache cookbook** (low complexity)
   - Memcached installation and configuration
   - Redis installation with authentication

3. **fastapi-tutorial cookbook** (high complexity)
   - PostgreSQL installation and database setup
   - Python environment setup
   - Application deployment
   - Systemd service configuration

### Assumptions

1. The target environment will continue to be Fedora 42 or compatible Linux distributions
2. Self-signed certificates are acceptable for the migrated solution (not using Let's Encrypt or other CA)
3. The same security hardening measures are required in the Ansible implementation
4. The FastAPI application source will continue to be pulled from the same Git repository
5. Redis and PostgreSQL passwords in the current implementation are hardcoded and will need to be moved to Ansible Vault
6. The current implementation assumes a single-server deployment model, which will be maintained

## Implementation Plan

### 1. Project Structure

Create the following Ansible project structure:

```
ansible-nginx-multisite/
├── inventory/
│   ├── hosts.ini
│   └── group_vars/
│       ├── all.yml
│       └── webservers.yml
├── roles/
│   ├── nginx_multisite/
│   ├── cache_services/
│   └── fastapi_app/
├── playbooks/
│   ├── site.yml
│   ├── nginx.yml
│   ├── cache.yml
│   └── fastapi.yml
└── vault/
    └── secrets.yml
```

### 2. Role Development

#### nginx_multisite role

- Implement Nginx installation and base configuration
- Create templates for site configurations
- Implement SSL certificate generation
- Configure security features (fail2ban, UFW)

#### cache_services role

- Implement Memcached installation and configuration
- Implement Redis installation with secure authentication
- Configure service dependencies

#### fastapi_app role

- Implement PostgreSQL installation and database setup
- Configure Python environment and dependencies
- Deploy FastAPI application
- Set up systemd service

### 3. Testing Strategy

- Use Vagrant with Ansible provisioner to test the migration
- Create equivalent test scenarios for each cookbook
- Verify SSL certificate generation and site accessibility
- Test security configurations

### 4. Documentation

- Create comprehensive README with usage instructions
- Document variables and their default values
- Provide examples for common customizations
- Include migration notes for Chef users

## Timeline Estimate

- **Week 1**: Analysis and initial role structure setup
- **Week 2**: Implement and test nginx_multisite role
- **Week 3**: Implement and test cache_services and fastapi_app roles
- **Week 4**: Integration testing, documentation, and handover

Total estimated effort: 3-4 weeks depending on complexity encountered during implementation.