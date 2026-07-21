# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with FastAPI application backend and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated complexity is medium, with an estimated timeline of 2-3 weeks for a complete migration.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

- **nginx-multisite**:
    - Description: Configures nginx with multiple SSL-enabled subdomains, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, fail2ban integration, UFW firewall configuration, security hardening

- **cache**:
    - Description: Configures caching services (memcached and redis) with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, log directory management

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks. Lists both local and external cookbook dependencies including nginx (~> 12.0), memcached (~> 6.0), and redisio (~> 7.2.4).
- `solo.json`: Chef configuration file defining the run list and node attributes for nginx sites and security configurations.
- `solo.rb`: Chef configuration file for Chef Solo.
- `Vagrantfile`: Defines the development VM configuration using Vagrant with Fedora 42, with port forwarding for HTTP (80→8080) and HTTPS (443→8443).
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef, installing dependencies, and running Chef Solo.

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0) as specified in cookbook metadata, but the Vagrantfile uses Fedora 42.
- **Virtual Machine Technology**: Vagrant with libvirt provider as specified in the Vagrantfile.
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment.

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` module or community.general collection
- **memcached (~> 6.0)**: Replace with Ansible's `memcached` module or community.general collection
- **redisio (~> 7.2.4)**: Replace with Ansible's `redis` module or community.general collection

### Security Considerations

- **SSL Certificate Management**: The current setup generates self-signed certificates for each site in nginx-multisite.
  - Migration approach: Use Ansible's `openssl_certificate`, `openssl_csr`, and `openssl_privatekey` modules from the `community.crypto` collection.

- **Firewall Configuration**: The current setup uses UFW for firewall management in nginx-multisite.
  - Migration approach: Use Ansible's `ufw` module for Ubuntu systems and `ansible.posix.firewalld` for RHEL/Fedora-based systems.

- **fail2ban Integration**: The current setup configures fail2ban for intrusion prevention in nginx-multisite.
  - Migration approach: Use Ansible's `template` module to configure fail2ban or a dedicated role from Ansible Galaxy.

- **SSH Hardening**: The current setup disables root login and password authentication in nginx-multisite.
  - Migration approach: Use Ansible's `lineinfile` module or `ansible.posix.sshd` module.

- **Vault/secrets management**: 
  - Redis password is hardcoded in the cache cookbook as 'redis_secure_password_123'
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook as 'fastapi_password'
  - Migration approach: Use Ansible Vault to encrypt sensitive values and reference them in playbooks

### Technical Challenges

- **Multi-site Nginx Configuration**: The current setup dynamically creates Nginx site configurations based on node attributes for test.cluster.local, ci.cluster.local, and status.cluster.local.
  - Mitigation: Use Ansible's template module with loops to achieve similar functionality.

- **SSL Certificate Generation**: The current setup generates self-signed certificates for each site.
  - Mitigation: Use Ansible's `openssl_*` modules to generate certificates or integrate with Let's Encrypt using `community.crypto`.

- **Service Dependencies**: The FastAPI application depends on PostgreSQL, and the Nginx configuration depends on the application services.
  - Mitigation: Use Ansible's handlers and meta dependencies to ensure proper service ordering.

- **Idempotent Database Setup**: The current setup uses raw SQL commands for database setup in fastapi-tutorial.
  - Mitigation: Use Ansible's `postgresql_*` modules for more idempotent database management.

### Migration Order

1. **cache** (low risk, moderate value): Start with the simplest cookbook that has external dependencies.
   - Create Ansible roles for memcached and redis configuration
   - Test independently before integrating with other services

2. **fastapi-tutorial** (moderate complexity): Next, migrate the application deployment.
   - Create Ansible roles for Python application deployment and PostgreSQL configuration
   - Test application functionality independently

3. **nginx-multisite** (high complexity, depends on other services): Finally, migrate the web server configuration.
   - Create Ansible roles for Nginx, SSL, and security configurations
   - Integrate with the previously migrated services

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS/RHEL-based systems.
2. The self-signed SSL certificates approach is acceptable for the migrated solution.
3. The current security configurations (fail2ban, UFW, SSH hardening) are required in the migrated solution.
4. The Vagrant development environment should be preserved or replaced with an equivalent Ansible-based setup.
5. The current directory structure with separate modules will be maintained in the Ansible roles.
6. The current hardcoded credentials will be replaced with Ansible Vault encrypted variables.
7. The current multi-site configuration approach will be maintained in the Ansible roles.