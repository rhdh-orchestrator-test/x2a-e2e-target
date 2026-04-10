# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This migration plan outlines the process of converting a Chef-based infrastructure to Ansible. The repository contains three Chef cookbooks managing a multi-site Nginx web server, caching services (Redis and Memcached), and a FastAPI Python application with PostgreSQL. The estimated complexity is moderate, with an estimated timeline of 4-6 weeks for complete migration, including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and custom configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw firewall)

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management file listing cookbook dependencies (nginx, ssl_certificate, memcached, redisio)
- `Policyfile.rb`: Chef policy file defining the run list and cookbook versions
- `solo.json`: Configuration data for Chef Solo, contains site configurations and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Defines a Fedora 42 VM for development/testing with port forwarding and networking
- `vagrant-provision.sh`: Bash script to provision the Vagrant VM with Chef

### Target Details

- **Operating System**: Fedora 42 (primary) with support for Ubuntu 18.04+ and CentOS 7+ based on cookbook metadata
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role (e.g., geerlingguy.nginx)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible redis role (e.g., geerlingguy.redis)
- **ssl_certificate (~> 2.1)**: Replace with Ansible certificate management (ansible.posix.openssl_* modules)

### Security Considerations

- **SSL Certificate Management**: Migration must preserve self-signed certificate generation for development environments
- **Firewall Configuration**: UFW firewall rules need to be migrated to appropriate Ansible firewall modules
- **fail2ban Configuration**: Ensure fail2ban settings are preserved in Ansible tasks
- **SSH Hardening**: Maintain SSH security settings (disable root login, password authentication)
- **Redis Authentication**: Preserve Redis password authentication in the migration

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of multiple virtual hosts with SSL needs careful translation to Ansible templates
- **Service Orchestration**: Ensuring proper service restart notifications when configuration changes
- **PostgreSQL User/Database Management**: Proper idempotent handling of database creation and user permissions
- **Python Application Deployment**: Managing virtual environments and dependencies with Ansible

### Migration Order

1. **nginx-multisite cookbook** (moderate complexity)
   - Start with basic Nginx installation and configuration
   - Add SSL certificate generation
   - Implement virtual hosts configuration
   - Add security hardening features

2. **cache cookbook** (low complexity)
   - Implement Memcached configuration
   - Add Redis with authentication

3. **fastapi-tutorial cookbook** (high complexity)
   - Set up PostgreSQL database and user
   - Implement Python application deployment
   - Configure systemd service

### Assumptions

1. The target environment will continue to be Fedora/RHEL-based systems
2. Self-signed certificates are acceptable for development environments
3. The same security policies should be maintained in the Ansible implementation
4. The FastAPI application source code will remain available at the same Git repository
5. The directory structure for web content and application code will remain the same
6. The Redis password will need to be stored securely in Ansible Vault
7. The PostgreSQL credentials will need to be stored securely in Ansible Vault

## Implementation Details

### Ansible Structure

```
ansible/
├── inventory/
│   ├── hosts.yml
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

### Vault Strategy

Sensitive information currently hardcoded in Chef recipes should be moved to Ansible Vault:
- Redis authentication password
- PostgreSQL database credentials
- Any SSL private keys or certificates

### Testing Strategy

1. Create a parallel Vagrant environment for Ansible testing
2. Implement incremental testing of each role
3. Validate functionality against the original Chef implementation
4. Perform integration testing of all components

### Documentation Requirements

1. README with setup and usage instructions
2. Role-specific documentation
3. Variable reference documentation
4. Inventory structure documentation