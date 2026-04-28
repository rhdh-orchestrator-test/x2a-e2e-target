# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies, configuration templates, and security settings.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- **Total**: 5-7 weeks

**Complexity Assessment**: Medium
- Multiple interconnected services
- Security configurations that need careful migration
- External dependencies on community cookbooks

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw firewall)

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef configuration file defining the run list and node attributes
- `solo.rb`: Chef configuration file defining paths and log settings
- `Vagrantfile`: Defines a Fedora 42 VM for local development and testing
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role (e.g., geerlingguy.nginx)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible redis role (e.g., geerlingguy.redis)

### Security Considerations

- **Firewall Configuration**: The Chef cookbook configures UFW firewall rules that need to be migrated to Ansible firewall module
- **Fail2ban Setup**: Fail2ban configuration needs to be migrated to Ansible
- **SSH Hardening**: SSH security settings (disable root login, password authentication) need to be preserved
- **SSL Certificate Management**: Self-signed certificate generation needs to be migrated
- **Vault/secrets management**:
  - Redis password in cache cookbook (hardcoded as 'redis_secure_password_123')
  - PostgreSQL database credentials in fastapi-tutorial cookbook (hardcoded as 'fastapi_password')
  - No Chef Vault or encrypted data bags detected, but credentials should be moved to Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of multiple virtual hosts with SSL needs careful translation to Ansible templates
- **Service Orchestration**: The current setup has interdependent services (Nginx, Redis, Memcached, PostgreSQL, FastAPI) that need to be started in the correct order
- **SSL Certificate Generation**: The self-signed certificate generation logic needs to be replicated in Ansible
- **Security Hardening**: The comprehensive security settings need to be carefully migrated to maintain the same security posture

### Migration Order

1. **cache** (Priority 1): Relatively simple cookbook with Redis and Memcached configuration
2. **nginx-multisite** (Priority 2): Core infrastructure component with security configurations
3. **fastapi-tutorial** (Priority 3): Application deployment that depends on the database and potentially the cache services

### Assumptions

1. The target environment will continue to be Fedora-based systems (specifically Fedora 42 as indicated in the Vagrantfile)
2. The same directory structure for web content will be maintained (/var/www/[site])
3. Self-signed certificates are acceptable for the migrated solution (production would likely use Let's Encrypt or other CA)
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current hardcoded credentials will be replaced with Ansible Vault secured variables
6. The same security posture (fail2ban, ufw, SSH hardening) is required in the Ansible solution
7. The Vagrant development environment should be preserved with equivalent functionality

## Ansible Structure Recommendation

```
ansible-nginx-multisite/
├── inventories/
│   ├── development/
│   │   ├── group_vars/
│   │   │   └── all/
│   │   │       ├── vars.yml
│   │   │       └── vault.yml
│   │   └── hosts.yml
│   └── production/
├── roles/
│   ├── nginx_multisite/
│   ├── cache_services/
│   ├── fastapi_app/
│   └── security/
├── playbooks/
│   ├── site.yml
│   ├── nginx.yml
│   ├── cache.yml
│   └── fastapi.yml
├── Vagrantfile
└── ansible.cfg
```

## Testing Strategy

1. Develop and test each role individually using Molecule
2. Create integration tests to verify interactions between components
3. Use the existing Vagrant setup to validate the full stack deployment
4. Compare the output of the Chef and Ansible deployments to ensure equivalence

## Knowledge Transfer Plan

1. Document each Ansible role with README files explaining purpose and configuration options
2. Create a migration report comparing the Chef and Ansible implementations
3. Conduct a walkthrough session with the team to explain the migration approach
4. Provide examples of common tasks and troubleshooting procedures