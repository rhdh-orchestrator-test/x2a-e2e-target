# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site web application environment with caching services and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks with their dependencies, configuration templates, and security settings. The estimated complexity is moderate, with an estimated timeline of 3-4 weeks for a complete migration.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and fail2ban/ufw firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, firewall configuration

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef configuration file containing the run list and node attributes
- `solo.rb`: Chef configuration file specifying cookbook paths and log settings
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Vagrant configuration file for local development environment

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for local development/testing

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for development
  - Migration should maintain proper certificate permissions (640) and ownership (root:ssl-cert)

- **Firewall Configuration**: 
  - UFW firewall rules need to be migrated to Ansible ufw module
  - Default deny policy with specific allow rules for SSH, HTTP, and HTTPS

- **Fail2ban Configuration**: 
  - Fail2ban setup needs to be migrated to Ansible fail2ban module or tasks

- **SSH Hardening**:
  - Disable root login
  - Disable password authentication
  - These settings should be migrated to Ansible ssh_config module

- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook
  - These should be migrated to Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - The dynamic generation of multiple virtual hosts based on node attributes needs to be carefully migrated to Ansible templates and loops
  - Solution: Use Ansible with_items/loop constructs with templates

- **SSL Certificate Generation**:
  - Self-signed certificate generation logic needs to be preserved
  - Solution: Use Ansible openssl_* modules

- **Service Dependencies**:
  - Ensuring proper service dependencies and restart notifications
  - Solution: Use Ansible handlers and meta dependencies

- **PostgreSQL User/Database Creation**:
  - The current implementation uses direct shell commands
  - Solution: Use Ansible postgresql_* modules for better idempotence

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Start with basic Nginx installation and configuration
   - Then add SSL and security features
   - Finally, implement multi-site configuration

2. **cache** (Priority 2)
   - Memcached and Redis services
   - Implement with proper security configurations

3. **fastapi-tutorial** (Priority 3)
   - Application deployment with database dependencies
   - Requires PostgreSQL setup and Python environment configuration

### Assumptions

1. The target environment will continue to be Fedora-based systems
2. Self-signed certificates are acceptable for the migrated solution (production would likely use Let's Encrypt or other CA)
3. The current security configurations are appropriate for the target environment
4. The FastAPI application repository will remain available at the specified URL
5. The current Redis and PostgreSQL passwords are development passwords and will be replaced with proper secrets management
6. The current directory structure in the target system (/opt/server/*, /var/www/*) should be maintained
7. The Vagrant development environment will be maintained or replaced with an equivalent

## Ansible Structure Recommendation

```
ansible-nginx-multisite/
├── inventories/
│   ├── development/
│   │   ├── group_vars/
│   │   │   └── all.yml  # Development environment variables
│   │   └── hosts        # Development inventory
│   └── production/
│       ├── group_vars/
│       │   └── all.yml  # Production environment variables
│       └── hosts        # Production inventory
├── roles/
│   ├── nginx-multisite/
│   │   ├── defaults/
│   │   ├── handlers/
│   │   ├── tasks/
│   │   └── templates/
│   ├── cache/
│   │   ├── defaults/
│   │   ├── handlers/
│   │   ├── tasks/
│   │   └── templates/
│   └── fastapi-tutorial/
│       ├── defaults/
│       ├── handlers/
│       ├── tasks/
│       └── templates/
├── playbooks/
│   ├── site.yml         # Main playbook
│   ├── nginx.yml        # Nginx-specific playbook
│   ├── cache.yml        # Cache services playbook
│   └── fastapi.yml      # FastAPI application playbook
├── requirements.yml     # External role dependencies
└── vagrant/
    └── Vagrantfile      # For local development
```

## Timeline Estimate

- **Analysis and Planning**: 3-5 days
- **Role Development**:
  - nginx-multisite: 5-7 days
  - cache: 3-4 days
  - fastapi-tutorial: 4-5 days
- **Testing and Validation**: 5-7 days
- **Documentation and Knowledge Transfer**: 2-3 days

**Total Estimated Timeline**: 3-4 weeks