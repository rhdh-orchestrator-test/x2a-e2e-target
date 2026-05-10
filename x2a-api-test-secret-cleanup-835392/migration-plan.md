# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site web application environment with caching services and a FastAPI application. The migration to Ansible will involve converting 3 Chef cookbooks, handling external dependencies, and ensuring proper security configurations are maintained.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- Multiple interconnected services
- Security configurations that need careful migration
- External dependencies on community cookbooks

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site-specific configurations
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
    - Key Features: Python virtual environment setup, Git-based deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks. Lists both local and external cookbook dependencies with version constraints.
- `solo.json`: Chef configuration file containing the run list and node attributes. Defines Nginx sites and security configurations.
- `solo.rb`: Chef configuration file specifying file paths and log settings.
- `Vagrantfile`: Defines a Vagrant VM configuration using Fedora 42 with port forwarding and resource allocation.
- `vagrant-provision.sh`: Shell script that installs Chef and Berkshelf, then runs Chef Solo to provision the VM.

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), but the Vagrantfile specifies Fedora 42 as the development environment.
- **Virtual Machine Technology**: Vagrant with libvirt provider (based on Vagrantfile configuration).
- **Cloud Platform**: Not specified in the repository. The configuration appears to be designed for on-premises or generic cloud VMs.

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` role or use the `ansible.builtin.package` module with templates
- **memcached (~> 6.0)**: Replace with Ansible's `memcached` role or use the `ansible.builtin.package` module with templates
- **redisio (~> 7.2.4)**: Replace with Ansible's `redis` role or use the `ansible.builtin.package` module with templates

### Security Considerations

- **SSL Certificate Management**: 
  - The current implementation generates self-signed certificates
  - Migration approach: Use Ansible's `openssl_*` modules or `community.crypto` collection

- **Firewall Configuration (UFW)**:
  - Migration approach: Use Ansible's `community.general.ufw` module

- **Fail2ban Configuration**:
  - Migration approach: Use Ansible's `community.general.fail2ban` module or template configuration files

- **SSH Hardening**:
  - Migration approach: Use Ansible's `ansible.posix.sshd_config` module or templates

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe (`redis_secure_password_123`)
  - PostgreSQL password is hardcoded in the recipe (`fastapi_password`)
  - Migration approach: Use Ansible Vault to secure these credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current implementation dynamically generates site configurations based on node attributes
  - Mitigation: Use Ansible templates with loops to generate site configurations from variables

- **Service Orchestration**:
  - Description: The current implementation has interdependent services (Nginx, Redis, Memcached, PostgreSQL, FastAPI)
  - Mitigation: Use Ansible handlers and proper dependency management to ensure services are started in the correct order

- **SSL Certificate Generation**:
  - Description: Self-signed certificates are generated for each site
  - Mitigation: Use Ansible's `community.crypto` collection for certificate generation or integrate with Let's Encrypt

### Migration Order

1. **cache** (Priority 1 - low complexity)
   - Simple configuration of Memcached and Redis
   - Few dependencies
   - Good starting point to establish patterns

2. **nginx-multisite** (Priority 2 - medium complexity)
   - Core infrastructure component
   - Multiple templates and configurations
   - Security configurations

3. **fastapi-tutorial** (Priority 3 - medium complexity)
   - Application deployment
   - Depends on PostgreSQL
   - Requires environment configuration

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS/RHEL-based distributions.
2. Self-signed certificates are acceptable for the migrated solution (no requirement for Let's Encrypt integration).
3. The current security configurations (fail2ban, UFW, SSH hardening) are required in the migrated solution.
4. The FastAPI application source will continue to be pulled from the same Git repository.
5. The current Redis and PostgreSQL passwords are for development only and will be replaced with secure passwords in production.
6. The Vagrant development environment is not required to be migrated to Ansible (could be kept as-is or replaced with Molecule for testing).