# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx configuration with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 3 weeks
- Testing and Validation: 2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 7 weeks

**Complexity Assessment:** Medium
- The codebase is well-structured with clear separation of concerns
- No custom resources or complex Chef-specific patterns are used
- External dependencies on community cookbooks will need Ansible equivalents

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
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
- `Policyfile.rb`: Chef Policyfile defining the run list and cookbook dependencies
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings
- `solo.json`: Node attributes and run list for Chef Solo
- `Vagrantfile`: Vagrant configuration for local development/testing using Fedora 42
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (primary) with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata and Vagrantfile)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` role or the `geerlingguy.nginx` community role
- **memcached (~> 6.0)**: Replace with Ansible's `memcached` module or the `geerlingguy.memcached` community role
- **redisio (~> 7.2.4)**: Replace with Ansible's `redis` module or the `geerlingguy.redis` community role
- **ssl_certificate (~> 2.1)**: Replace with Ansible's `openssl_*` modules for certificate management

### Security Considerations

- **SSL Certificate Management**: The current setup generates self-signed certificates. Migrate to Ansible's `openssl_certificate` module with options for Let's Encrypt integration.
- **Firewall Configuration**: UFW configuration should be migrated to Ansible's `ufw` module or `firewalld` module for Fedora/CentOS.
- **fail2ban Setup**: Migrate to Ansible's `template` module for fail2ban configuration.
- **SSH Hardening**: Migrate SSH security settings using Ansible's `lineinfile` or `template` modules.
- **Redis Password**: The Redis password is hardcoded in the recipe. Use Ansible Vault to secure this credential.

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of site configurations based on node attributes will need to be replicated using Ansible's templating system.
- **SSL Certificate Generation**: Self-signed certificate generation logic needs to be migrated to Ansible's `openssl_*` modules.
- **PostgreSQL User/Database Creation**: The current implementation uses direct `psql` commands. This should be migrated to Ansible's `postgresql_*` modules.
- **Python Application Deployment**: The git clone, venv creation, and dependency installation will need to be migrated to Ansible's equivalent modules.

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Start with basic Nginx installation and configuration
   - Add SSL certificate generation
   - Implement security hardening (fail2ban, UFW)
   - Configure virtual hosts

2. **cache** (low complexity, standalone service)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Set up PostgreSQL
   - Deploy Python application
   - Configure systemd service

### Assumptions

1. The target environment will continue to be Fedora-based, with potential for Ubuntu/CentOS deployment
2. Self-signed certificates are acceptable for development/testing (production would likely use proper certificates)
3. The current security configurations (fail2ban, UFW, SSH hardening) are appropriate for the target environment
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The Redis password in the current configuration is for development purposes and will be replaced with a secure password in production

## Ansible Structure Recommendation

```
ansible-nginx-multisite/
├── inventories/
│   ├── development/
│   │   ├── hosts.yml
│   │   └── group_vars/
│   └── production/
│       ├── hosts.yml
│       └── group_vars/
├── roles/
│   ├── nginx-multisite/
│   ├── cache/
│   └── fastapi-tutorial/
├── playbooks/
│   ├── site.yml
│   ├── nginx.yml
│   ├── cache.yml
│   └── fastapi.yml
├── group_vars/
│   └── all/
│       ├── main.yml
│       └── vault.yml
└── ansible.cfg
```

## Testing Strategy

1. Create Vagrant-based test environment similar to the current setup
2. Develop individual role tests using Molecule
3. Implement integration tests for the complete stack
4. Validate functionality against the original Chef implementation

## Knowledge Transfer Plan

1. Document each Ansible role with README files explaining purpose and configuration options
2. Create example playbooks demonstrating common usage patterns
3. Provide mapping documentation showing Chef cookbook to Ansible role equivalents
4. Conduct knowledge transfer sessions with the team