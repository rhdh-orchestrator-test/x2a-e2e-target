# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure for deploying a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI application with PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 3 weeks
- Testing and Validation: 2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 7 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- External dependencies on community cookbooks need to be replaced with Ansible Galaxy roles
- Security configurations and SSL certificate management require careful handling
- Secrets management needs to be improved during migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and site configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw, sysctl)

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment, Git repository deployment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks. Lists both local and external dependencies including nginx (~> 12.0), memcached (~> 6.0), and redisio (~> 7.2.4).
- `solo.json`: Chef configuration file defining the run list and node attributes. Contains configuration for nginx sites, SSL paths, and security settings.
- `solo.rb`: Chef configuration file specifying cookbook paths and log settings.
- `Vagrantfile`: Defines a Fedora 42 VM with port forwarding for development and testing.
- `vagrant-provision.sh`: Shell script to install Chef and run the cookbooks in the Vagrant environment.

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0) as specified in cookbook metadata. The Vagrantfile uses Fedora 42.
- **Virtual Machine Technology**: Vagrant with libvirt provider as indicated in the Vagrantfile.
- **Cloud Platform**: Not specified in the repository. The configuration appears to be designed for on-premises or generic cloud VMs.

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Ansible role
- **memcached (~> 6.0)**: Replace with Ansible Galaxy role `geerlingguy.memcached`
- **redisio (~> 7.2.4)**: Replace with Ansible Galaxy role `geerlingguy.redis` or DavidWittman.redis

### Security Considerations

- **SSL Certificate Management**: 
  - The current implementation generates self-signed certificates
  - Migration approach: Use Ansible's `openssl_*` modules for certificate generation or integrate with Let's Encrypt using `geerlingguy.certbot`

- **Firewall Configuration (UFW)**:
  - Migration approach: Use Ansible's `ufw` module to configure firewall rules

- **Fail2ban Configuration**:
  - Migration approach: Create an Ansible role for fail2ban configuration using templates

- **SSH Hardening**:
  - Migration approach: Use Ansible's `lineinfile` module or the `ansible.posix.sshd` module to configure SSH security settings

- **Vault/secrets management**:
  - Credentials detected:
    - Redis password in cache cookbook: "redis_secure_password_123"
    - PostgreSQL credentials in fastapi-tutorial cookbook: User "fastapi" with password "fastapi_password"
  - Migration approach: Use Ansible Vault to encrypt sensitive values

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current implementation uses Chef templates to generate site configurations dynamically
  - Mitigation: Create Ansible templates with similar logic using Jinja2 templating

- **Redis Configuration Hack**: 
  - Description: The cache cookbook includes a ruby_block to modify Redis configuration files after they're created
  - Mitigation: Create a custom Redis configuration template in Ansible that properly handles these settings

- **PostgreSQL User and Database Creation**:
  - Description: The current implementation uses shell commands via execute resources
  - Mitigation: Use Ansible's `postgresql_*` modules for more idiomatic database management

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Moderate complexity with security configurations and SSL management

2. **cache** (Priority 2)
   - Dependent services that can be migrated after the web server
   - Moderate complexity with Redis configuration requiring special attention

3. **fastapi-tutorial** (Priority 3)
   - Application deployment that depends on PostgreSQL
   - Higher complexity with Python environment, Git deployment, and database setup

### Assumptions

1. The target environment will continue to be Fedora/CentOS/Ubuntu Linux systems
2. Self-signed certificates are acceptable for development/testing (production would likely use proper certificates)
3. The current security configurations (fail2ban, ufw, SSH hardening) are appropriate for the target environment
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current hardcoded credentials will be replaced with more secure practices in the Ansible implementation
6. The Vagrant development environment will be maintained for testing the Ansible playbooks
7. No custom Chef resources or libraries are being used that would require special handling
8. The current directory structure in the target environment (/opt/fastapi-tutorial, /etc/ssl/certs, etc.) will be maintained