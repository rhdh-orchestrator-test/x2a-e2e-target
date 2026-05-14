# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup with three primary cookbooks: nginx-multisite, cache, and fastapi-tutorial. The migration to Ansible will involve converting these cookbooks to Ansible roles and playbooks while maintaining the same functionality. The repository is of moderate complexity with clear separation of concerns between the cookbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw), custom Nginx configuration

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, log directory management

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks. Lists both local and external cookbook dependencies with version constraints. Will be replaced by Ansible Galaxy requirements.yml.
- `solo.json`: Chef node configuration with run list and attribute overrides. Will be replaced by Ansible inventory variables.
- `solo.rb`: Chef Solo configuration file. Will be replaced by Ansible configuration.
- `Vagrantfile`: Defines the development VM using Fedora 42. Can be adapted to use Ansible provisioner instead of Chef.
- `vagrant-provision.sh`: Shell script to install Chef and run the cookbooks. Will be replaced with Ansible provisioning.

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0) based on cookbook metadata. Development environment uses Fedora 42 (from Vagrantfile).
- **Virtual Machine Technology**: Vagrant with libvirt provider (based on Vagrantfile configuration).
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment.

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` role or direct package installation and configuration
- **memcached (~> 6.0)**: Replace with Ansible's `geerlingguy.memcached` role or direct package management
- **redisio (~> 7.2.4)**: Replace with Ansible's `geerlingguy.redis` role or direct package management
- **PostgreSQL**: Replace with Ansible's `geerlingguy.postgresql` role or direct package management

### Security Considerations

- **SSL Certificate Management**: 
  - Migration approach: Use Ansible's `openssl_*` modules to generate self-signed certificates
  - Consider integration with `community.crypto` collection for more advanced certificate management

- **Firewall Configuration (UFW)**:
  - Migration approach: Use Ansible's `ufw` module to configure firewall rules
  - Ensure idempotent rule application

- **Fail2ban Configuration**:
  - Migration approach: Use Ansible to deploy fail2ban configuration templates
  - Ensure service is enabled and running

- **SSH Hardening**:
  - Migration approach: Use Ansible's `lineinfile` module to modify SSH configuration
  - Consider using `ansible.posix.sysctl` module for kernel parameter configuration

- **Vault/secrets management**:
  - Redis password in cache cookbook (hardcoded as 'redis_secure_password_123')
  - PostgreSQL database credentials in fastapi-tutorial cookbook (hardcoded as 'fastapi_password')
  - Consider using Ansible Vault to secure these credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current implementation dynamically generates site configurations based on node attributes
  - Mitigation: Use Ansible templates with loops to generate site configurations from variables

- **SSL Certificate Generation**:
  - Description: Self-signed certificates are generated for each site
  - Mitigation: Use Ansible's `openssl_certificate` module with proper idempotency checks

- **Redis Configuration Patching**:
  - Description: The current implementation uses a ruby_block to modify Redis configuration files after they're created
  - Mitigation: Create a proper template for Redis configuration instead of modifying files after creation

- **PostgreSQL User and Database Creation**:
  - Description: Currently using shell commands via execute resource
  - Mitigation: Use Ansible's `postgresql_*` modules for proper idempotent database management

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for web services)
   - Start with basic Nginx installation and configuration
   - Add SSL certificate generation
   - Implement security hardening (fail2ban, ufw)
   - Configure virtual hosts

2. **cache** (low complexity, standalone service)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, application deployment)
   - Set up PostgreSQL database
   - Deploy Python application from Git
   - Configure virtual environment and dependencies
   - Set up systemd service

### Assumptions

1. The target environment will continue to be Vagrant with libvirt for development/testing
2. Self-signed certificates are acceptable for the migrated solution (production would likely use Let's Encrypt or other CA)
3. The same operating system support (Ubuntu 18.04+ and CentOS 7+) is required
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current security configurations (fail2ban, ufw, SSH hardening) are appropriate for the target environment
6. Redis and PostgreSQL passwords in the code are development passwords and will be replaced with secure values in production
7. The Nginx sites configuration in solo.json (test.cluster.local, ci.cluster.local, status.cluster.local) will remain the same
8. The current port mappings and networking configuration in Vagrant will be maintained