# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The repository has well-structured Chef cookbooks with clear responsibilities
- External dependencies on community cookbooks need to be replaced with Ansible Galaxy roles
- Security configurations and SSL certificate management require careful migration

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
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository deployment, Python virtual environment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks. Lists both local and external cookbook dependencies with version constraints.
- `solo.json`: Chef configuration file defining the run list and node attributes. Contains configuration for nginx sites and security settings.
- `solo.rb`: Chef configuration file specifying file paths and log settings.
- `Vagrantfile`: Defines a Vagrant VM configuration using Fedora 42 with port forwarding and resource allocation.
- `vagrant-provision.sh`: Shell script that installs Chef and runs the cookbooks in the Vagrant environment.

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), but the Vagrantfile specifies Fedora 42 as the development environment.
- **Virtual Machine Technology**: Vagrant with libvirt provider (based on Vagrantfile configuration).
- **Cloud Platform**: Not specified in the repository. The configuration appears to be designed for on-premises or generic cloud VMs.

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` role from Galaxy or direct package installation and configuration
- **memcached (~> 6.0)**: Replace with Ansible's `geerlingguy.memcached` role or direct package management
- **redisio (~> 7.2.4)**: Replace with Ansible's `geerlingguy.redis` or DavidWittman.redis role

### Security Considerations

- **SSL Certificate Management**: 
  - The current implementation generates self-signed certificates
  - Migration approach: Use Ansible's `openssl_*` modules or community.crypto collection

- **Firewall Configuration (UFW)**:
  - Migration approach: Use Ansible's `ufw` module to configure firewall rules

- **Fail2ban Configuration**:
  - Migration approach: Use Ansible to install and configure fail2ban with templates

- **SSH Hardening**:
  - Migration approach: Use Ansible's `lineinfile` module or the `ansible-hardening` role

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the FastAPI recipe (`fastapi:fastapi_password`)
  - Migration approach: Use Ansible Vault to securely store and manage these credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current implementation dynamically generates Nginx site configurations based on node attributes
  - Mitigation: Create Ansible templates with loops to generate site configurations from variables

- **SSL Certificate Generation**:
  - Description: Self-signed certificates are generated for each site
  - Mitigation: Use Ansible's `openssl_certificate` module with proper idempotency checks

- **Redis Configuration Patching**:
  - Description: The Chef recipe includes a hack to modify Redis configuration after installation
  - Mitigation: Create a proper Redis configuration template in Ansible instead of post-installation patching

- **PostgreSQL User and Database Creation**:
  - Description: Uses shell commands via execute resource
  - Mitigation: Use Ansible's `postgresql_*` modules for better idempotency and error handling

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Start with basic Nginx installation and configuration
   - Add security hardening (fail2ban, ufw, sysctl)
   - Implement SSL certificate generation
   - Configure virtual hosts

2. **cache** (low complexity, independent service)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Set up PostgreSQL
   - Deploy FastAPI application
   - Configure systemd service

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS/RHEL-based distributions.
2. Self-signed certificates are acceptable for the migrated solution (no integration with Let's Encrypt or other CA).
3. The current security configurations are sufficient and no additional hardening is required.
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
5. The current Redis and Memcached configurations are optimal and don't need performance tuning during migration.
6. The Vagrant development environment will be maintained for testing the Ansible playbooks.
7. No CI/CD pipeline integration is required as part of the migration.