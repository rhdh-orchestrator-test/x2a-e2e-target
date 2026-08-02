# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with caching services and a FastAPI application. The migration to Ansible will involve converting 3 Chef cookbooks with their recipes, templates, and attributes to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- No complex custom resources or libraries
- Standard infrastructure components (Nginx, Redis, Memcached, PostgreSQL)
- Security configurations that need careful migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw), custom Nginx configurations

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies including external cookbooks from Chef Supermarket (nginx, memcached, redisio)
- `solo.json`: Contains node attributes and run list for Chef Solo
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Defines a Fedora 42 VM for local development and testing
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile configuration)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` role or direct package installation and configuration
- **memcached (~> 6.0)**: Replace with Ansible's `geerlingguy.memcached` role or direct package management
- **redisio (~> 7.2.4)**: Replace with Ansible's `geerlingguy.redis` role or direct Redis installation and configuration

### Security Considerations

- **Firewall Configuration**: The Chef cookbook configures UFW. Ansible should use the `ansible.posix.firewalld` or `community.general.ufw` module depending on the target OS.
- **Fail2Ban Setup**: The Chef cookbook configures fail2ban with custom jail settings. Ansible should use the `community.general.fail2ban` module.
- **SSH Hardening**: The Chef cookbook disables root login and password authentication. Ansible should use the `ansible.posix.sshd` module.
- **System Hardening**: The Chef cookbook applies sysctl security settings. Ansible should use the `ansible.posix.sysctl` module.
- **Vault/secrets management**:
  - Redis password in the cache cookbook: "redis_secure_password_123"
  - PostgreSQL database credentials in the fastapi-tutorial cookbook: "fastapi_password"
  - SSL certificates and private keys generated and stored in `/etc/ssl/certs` and `/etc/ssl/private`

### Technical Challenges

- **SSL Certificate Generation**: The Chef cookbook generates self-signed certificates for each site. Ansible should use the `community.crypto.openssl_*` modules to replicate this functionality.
- **Multi-site Configuration**: The Chef cookbook dynamically creates Nginx site configurations based on node attributes. Ansible will need to use loops and templates to achieve the same result.
- **Service Dependencies**: The FastAPI application depends on PostgreSQL. Ansible will need to ensure proper service ordering and dependencies.
- **Idempotent Database Setup**: The Chef cookbook uses PostgreSQL commands to create users and databases. Ansible should use the `community.postgresql` modules for idempotent database management.

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Contains security configurations that should be applied first

2. **cache** (Priority 2)
   - Supporting services that the application may depend on
   - Relatively simple configuration with external dependencies

3. **fastapi-tutorial** (Priority 3)
   - Application deployment that depends on the infrastructure being in place
   - More complex with database setup, git repository management, and service configuration

### Assumptions

1. The target environment will continue to be Fedora 42 or a compatible Linux distribution.
2. The self-signed SSL certificates are acceptable for the migrated environment (not production).
3. The directory structure for web content and application code will remain the same.
4. The PostgreSQL database schema and data migration is out of scope for this infrastructure migration.
5. The Redis password and PostgreSQL credentials will be managed securely in Ansible Vault in the new implementation.
6. The FastAPI application code repository will remain available at the specified URL.
7. The Vagrant development environment will be replaced with an equivalent Ansible-based setup.