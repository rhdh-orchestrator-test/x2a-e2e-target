# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application with PostgreSQL. The migration scope includes three Chef cookbooks with moderate complexity. The estimated timeline for migration is 3-4 weeks, with the most complex components being the Nginx multi-site SSL configuration and the FastAPI application deployment.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled subdomains, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site virtual hosts, SSL configuration, security hardening (fail2ban, UFW)

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks. Lists both local and external cookbook dependencies with version constraints. Will be replaced by Ansible Galaxy requirements.yml.
- `Vagrantfile`: Defines a Fedora 42 VM for local development and testing. Can be adapted for Ansible Vagrant testing.
- `solo.json`: Chef node configuration with run list and attribute overrides. Will be replaced by Ansible inventory and group_vars.
- `solo.rb`: Chef Solo configuration file. Will be replaced by ansible.cfg.
- `vagrant-provision.sh`: Shell script to provision Chef in the Vagrant VM. Will be replaced by Ansible provisioning in Vagrantfile.

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0) based on cookbook metadata, with Fedora 42 used for development (from Vagrantfile).
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile configuration).
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs.

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role or redis_* modules

### Security Considerations

- **SSL Certificate Management**: The nginx-multisite cookbook manages SSL certificates in `/etc/ssl/certs` and `/etc/ssl/private`. Migration should use Ansible's crypto modules for certificate management.
- **Redis Authentication**: Redis is configured with password authentication (`redis_secure_password_123`). This should be migrated to Ansible Vault for secure storage.
- **Security Hardening**: The nginx-multisite cookbook implements several security measures:
  - fail2ban configuration
  - UFW firewall rules
  - SSH hardening (disabling root login, password authentication)
  - These should be implemented using appropriate Ansible security roles.
- **Vault/secrets management**:
  - Redis password in cache cookbook (hardcoded as `redis_secure_password_123`)
  - PostgreSQL database credentials in fastapi-tutorial cookbook (hardcoded as `fastapi:fastapi_password`)
  - Environment variables in .env file for FastAPI application

### Technical Challenges

- **Multi-site Nginx Configuration**: The nginx-multisite cookbook manages multiple virtual hosts with SSL. This will require careful template migration to Ansible.
- **Redis Configuration Patching**: The cache cookbook includes a ruby_block that modifies Redis configuration files after they're created. This will need a custom approach in Ansible.
- **FastAPI Application Deployment**: The fastapi-tutorial cookbook clones a Git repository and sets up a Python environment. This will require careful sequencing in Ansible.
- **SSL Certificate Generation**: Self-signed certificates are likely being generated for development. This process will need to be replicated in Ansible.

### Migration Order

1. **cache cookbook** (Priority 1, moderate complexity): Start with the caching services as they have fewer dependencies and provide a foundation for the application.
2. **nginx-multisite cookbook** (Priority 2, high complexity): Migrate the Nginx configuration next, as it's required for serving the application.
3. **fastapi-tutorial cookbook** (Priority 3, high complexity): Finally, migrate the application deployment, which depends on both the web server and caching services.

### Assumptions

1. Self-signed SSL certificates are being used for development purposes. Production environments may require integration with Let's Encrypt or another certificate provider.
2. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git is publicly accessible and will remain available.
3. The current setup is designed for a single-server deployment, not a distributed architecture.
4. No custom Chef resources or libraries are being used that would require special handling in Ansible.
5. The security configurations (fail2ban, UFW, SSH hardening) are standard and can be implemented with existing Ansible roles.
6. The Redis configuration patching is a workaround for compatibility issues that may not be necessary with a direct Ansible Redis role.
7. No complex Chef search or data bag features are being used that would require special handling in Ansible.
8. The Vagrant setup is primarily for development and testing, not production deployment.