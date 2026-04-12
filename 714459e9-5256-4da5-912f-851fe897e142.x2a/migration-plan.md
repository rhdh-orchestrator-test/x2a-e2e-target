# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three primary cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- Well-structured Chef cookbooks with clear separation of concerns
- Standard infrastructure components (Nginx, Redis, Memcached, PostgreSQL)
- Some security configurations that require careful migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and site configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw)

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository deployment, Python virtual environment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks, lists external dependencies from Chef Supermarket
- `Policyfile.rb`: Chef Policyfile defining the run list and cookbook dependencies
- `solo.json`: Node attributes and configuration data for Chef Solo
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Defines the development VM using Fedora 42, with port forwarding and network configuration
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with Fedora 42 used in development
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role (e.g., geerlingguy.nginx)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible redis role (e.g., geerlingguy.redis)
- **ssl_certificate (~> 2.1)**: Replace with Ansible certificate generation tasks using openssl module

### Security Considerations

- **SSL Certificate Management**: Migration must preserve the self-signed certificate generation for development environments
- **Firewall Configuration (ufw)**: Convert ufw rules to Ansible's ufw module
- **fail2ban Configuration**: Migrate fail2ban configuration to Ansible tasks
- **SSH Hardening**: Preserve SSH security settings (disable root login, password authentication)
- **Redis Authentication**: Ensure Redis password is properly managed in Ansible Vault
- **PostgreSQL Credentials**: Store database credentials in Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: Ensure the dynamic generation of site configurations is preserved in Ansible
- **SSL Certificate Generation**: Implement equivalent SSL certificate generation logic in Ansible
- **Service Dependencies**: Maintain proper ordering of service installations and configurations
- **Redis Configuration Hacks**: Address the Redis configuration workarounds in a cleaner way with Ansible

### Migration Order

1. **Base Infrastructure** (low complexity)
   - Vagrant environment setup
   - Basic system configuration

2. **nginx-multisite** (medium complexity)
   - Nginx installation and configuration
   - SSL certificate generation
   - Security hardening (fail2ban, ufw)

3. **cache** (medium complexity)
   - Memcached configuration
   - Redis installation and security setup

4. **fastapi-tutorial** (high complexity)
   - PostgreSQL installation and configuration
   - Python environment setup
   - Application deployment
   - Service configuration

### Assumptions

1. The target environment will continue to be Fedora/CentOS/Ubuntu based systems
2. Self-signed certificates are acceptable for development environments
3. The same security practices should be maintained in the Ansible implementation
4. The FastAPI application source will continue to be pulled from the same Git repository
5. The Redis password and PostgreSQL credentials will need to be stored securely in Ansible Vault
6. The multi-site configuration for Nginx will maintain the same structure and naming conventions

## Ansible Implementation Plan

### Directory Structure

```
ansible/
├── inventories/
│   ├── development/
│   │   ├── hosts.yml
│   │   └── group_vars/
│   │       ├── all.yml
│   │       └── webservers.yml
│   └── production/
│       ├── hosts.yml
│       └── group_vars/
│           ├── all.yml
│           └── webservers.yml
├── roles/
│   ├── nginx_multisite/
│   │   ├── defaults/
│   │   ├── handlers/
│   │   ├── tasks/
│   │   ├── templates/
│   │   └── files/
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
└── vagrant/
    ├── Vagrantfile
    └── provision.yml
```

### Key Ansible Components

1. **Roles**:
   - `nginx_multisite`: Nginx installation, configuration, SSL, and security
   - `cache_services`: Memcached and Redis installation and configuration
   - `fastapi_app`: FastAPI application deployment with PostgreSQL

2. **Playbooks**:
   - `site.yml`: Main playbook that includes all roles
   - `nginx.yml`: Nginx-specific playbook
   - `cache.yml`: Cache services playbook
   - `fastapi.yml`: FastAPI application playbook

3. **Variables**:
   - Store sensitive information in Ansible Vault
   - Maintain the same configuration structure as in Chef attributes

4. **Templates**:
   - Convert Chef templates to Ansible Jinja2 templates
   - Maintain the same configuration parameters

### Testing Strategy

1. Develop a Vagrant-based testing environment similar to the existing one
2. Create test playbooks to validate each role independently
3. Implement integration tests to verify the complete stack
4. Compare the results with the existing Chef implementation

### Documentation

1. Document each Ansible role with README files
2. Provide examples for common configuration scenarios
3. Include migration notes for Chef users transitioning to Ansible