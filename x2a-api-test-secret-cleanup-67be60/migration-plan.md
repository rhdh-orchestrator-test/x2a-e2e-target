# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The repository has well-structured Chef cookbooks with clear dependencies
- Security configurations are present and need careful migration
- Multiple services need to be orchestrated (Nginx, Redis, Memcached, PostgreSQL, FastAPI)

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, fail2ban integration, UFW firewall

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies including nginx (~> 12.0), memcached (~> 6.0), and redisio (~> 7.2.4)
- `Vagrantfile`: Defines development VM using Fedora 42, with port forwarding and resource allocation
- `solo.json`: Chef configuration with run list and node attributes for Nginx sites and security settings
- `solo.rb`: Chef Solo configuration with cookbook paths and log settings
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create custom Nginx role
- **memcached (~> 6.0)**: Replace with Ansible Galaxy role `geerlingguy.memcached`
- **redisio (~> 7.2.4)**: Replace with Ansible Galaxy role `geerlingguy.redis` or DavidWittman.redis

### Security Considerations

- **SSL Certificate Management**: 
  - Chef cookbook generates self-signed certificates
  - Migration approach: Use Ansible `openssl_*` modules or community.crypto collection

- **Firewall Configuration**: 
  - Chef cookbook configures UFW with specific rules
  - Migration approach: Use Ansible `ufw` module to replicate rules

- **fail2ban Integration**: 
  - Chef cookbook installs and configures fail2ban
  - Migration approach: Use Ansible to deploy fail2ban configuration templates

- **SSH Hardening**: 
  - Chef cookbook disables root login and password authentication
  - Migration approach: Use Ansible `lineinfile` module or dedicated ssh role

- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook
  - Migration approach: Use Ansible Vault to secure these credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The Chef cookbook dynamically creates multiple virtual hosts with SSL
  - Mitigation: Create Ansible templates with Jinja2 loops to generate site configurations

- **Service Orchestration**: 
  - Description: Multiple interdependent services need to be configured in the right order
  - Mitigation: Use Ansible handlers and proper dependency management between roles

- **SSL Certificate Generation**: 
  - Description: Self-signed certificates are generated for each site
  - Mitigation: Use Ansible's crypto modules to generate certificates or integrate with Let's Encrypt

- **Database Initialization**: 
  - Description: PostgreSQL database and user creation for FastAPI
  - Mitigation: Use Ansible's PostgreSQL modules to create databases and users

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Create base Nginx configuration and security hardening

2. **cache** (Priority 2)
   - Implement Memcached and Redis configurations
   - Secure Redis with password authentication

3. **fastapi-tutorial** (Priority 3)
   - Set up PostgreSQL database
   - Deploy FastAPI application
   - Configure systemd service

### Assumptions

1. The target environment will continue to be Fedora-based systems (specifically Fedora 42 as specified in the Vagrantfile)
2. Self-signed certificates are acceptable for development/testing (production would likely use proper certificates)
3. The security requirements (fail2ban, UFW, SSH hardening) will remain the same
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The Redis and PostgreSQL passwords in the current configuration are for development only and will be replaced with secure passwords in production
6. The current Nginx site configuration (test.cluster.local, ci.cluster.local, status.cluster.local) will be maintained
7. The current port mappings (80/443 internally, 8080/8443 forwarded) will be maintained