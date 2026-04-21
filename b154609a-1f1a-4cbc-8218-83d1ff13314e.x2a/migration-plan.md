# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies, configuration templates, and security settings.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1 week
- Documentation and Knowledge Transfer: 1 week
- **Total**: 5-6 weeks

**Complexity Assessment**: Medium
- Well-structured Chef cookbooks with clear separation of concerns
- Standard web server, caching, and application deployment patterns
- Security configurations that need careful migration
- Secrets management needs improvement in the Ansible implementation

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and custom configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, fail2ban integration, UFW firewall configuration

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, log directory management

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository deployment, Python virtual environment setup, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies including nginx (~> 12.0), memcached (~> 6.0), and redisio (~> 7.2.4)
- `solo.json`: Defines the Chef run list and configuration attributes for nginx sites and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Defines a Fedora 42 VM for development/testing with port forwarding and resource allocation
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef

### Target Details

- **Operating System**: Fedora (based on Vagrantfile specifying "generic/fedora42"), with support for Ubuntu (>= 18.04) and CentOS (>= 7.0) mentioned in cookbook metadata
- **Virtual Machine Technology**: Libvirt (specified in Vagrantfile)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` module and community.general collection
- **memcached (~> 6.0)**: Use Ansible's package module and templates for configuration
- **redisio (~> 7.2.4)**: Use Ansible's package module and templates for Redis configuration with authentication
- **PostgreSQL**: Use Ansible's `postgresql_*` modules from the community.postgresql collection

### Security Considerations

- **SSL Certificate Management**: 
  - Current implementation generates self-signed certificates
  - Migration approach: Use Ansible's `openssl_*` modules for certificate generation or community.crypto collection

- **Firewall Configuration (UFW)**:
  - Current implementation enables UFW with specific rules for SSH, HTTP, and HTTPS
  - Migration approach: Use Ansible's `ufw` module from community.general collection

- **fail2ban Integration**:
  - Current implementation installs and configures fail2ban
  - Migration approach: Use Ansible's package module and templates for fail2ban configuration

- **System Hardening**:
  - Current implementation includes sysctl security settings
  - Migration approach: Use Ansible's `sysctl` module

- **SSH Hardening**:
  - Current implementation disables root login and password authentication
  - Migration approach: Use Ansible's `lineinfile` module or templates for SSH configuration

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe as 'redis_secure_password_123'
  - PostgreSQL password is hardcoded in the recipe as 'fastapi_password'
  - Migration approach: Use Ansible Vault for storing sensitive information

### Technical Challenges

- **Multi-site Nginx Configuration**:
  - Challenge: Replicating the dynamic site configuration from Chef to Ansible
  - Mitigation: Create Ansible templates with Jinja2 loops to iterate through site configurations

- **SSL Certificate Generation**:
  - Challenge: Ensuring proper permissions and security for SSL certificates
  - Mitigation: Use Ansible's file module with appropriate permissions and the openssl_* modules

- **Service Dependencies**:
  - Challenge: Ensuring proper service startup order (e.g., PostgreSQL before FastAPI)
  - Mitigation: Use Ansible handlers and meta dependencies between roles

- **Idempotent Database Creation**:
  - Challenge: Ensuring PostgreSQL database creation is idempotent
  - Mitigation: Use Ansible's postgresql_* modules instead of shell commands

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Start with basic Nginx installation
   - Add SSL certificate generation
   - Configure virtual hosts
   - Implement security hardening

2. **cache** (low complexity, independent service)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Set up PostgreSQL database
   - Deploy FastAPI application
   - Configure systemd service

### Assumptions

1. The target environment will continue to be Fedora-based, with potential support for Ubuntu and CentOS as mentioned in the cookbook metadata.
2. Self-signed certificates are acceptable for the migration (production environments would likely use Let's Encrypt or other CA-signed certificates).
3. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
4. The current security settings (fail2ban, UFW, SSH hardening) are appropriate for the target environment.
5. The Redis and PostgreSQL passwords in the current implementation are development passwords and will be replaced with more secure passwords in the Ansible implementation.
6. The current Nginx site configuration (test.cluster.local, ci.cluster.local, status.cluster.local) will remain the same in the Ansible implementation.
7. The Vagrant development environment will be maintained for testing the Ansible implementation.