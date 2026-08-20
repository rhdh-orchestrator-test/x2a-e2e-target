# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with FastAPI application and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated complexity is moderate, with an estimated timeline of 2-3 weeks for a complete migration, including testing and documentation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and self-signed certificates
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw)

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks. Lists both local and external cookbook dependencies.
- `solo.json`: Chef configuration data with node attributes for Nginx sites, SSL paths, and security settings.
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings.
- `vagrant-provision.sh`: Bash script for provisioning the Vagrant VM with Chef.
- `Vagrantfile`: Defines the development VM configuration using Fedora 42.

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with Fedora 42 used in the Vagrant development environment.
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile configuration).
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment.

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or collection (e.g., `ansible.posix.nginx`)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., `geerlingguy.memcached`)
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role (e.g., `geerlingguy.redis`)

### Security Considerations

- **SSL Certificate Management**: The current implementation generates self-signed certificates. Migration should use Ansible's `openssl_*` modules or community.crypto collection.
- **Firewall Configuration**: Replace UFW configuration with Ansible's `ufw` module or `ansible.posix.firewalld` for RHEL-based systems.
- **Fail2ban Configuration**: Migrate fail2ban configuration using Ansible's template module.
- **SSH Hardening**: Maintain SSH security configurations using Ansible's `lineinfile` or template modules.
- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook (`fastapi:fastapi_password`)
  - These should be migrated to Ansible Vault or an external secrets management solution

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of multiple Nginx sites will require careful templating in Ansible.
- **SSL Certificate Generation**: Self-signed certificate generation logic needs to be replicated using Ansible's crypto modules.
- **Service Dependencies**: Ensuring proper ordering of service deployments (PostgreSQL before FastAPI, etc.).
- **Platform Compatibility**: Maintaining support for both Debian/Ubuntu and RHEL/CentOS family systems.

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Start with basic Nginx installation
   - Add SSL certificate generation
   - Implement security hardening
   - Configure virtual hosts

2. **cache** (low complexity, standalone service)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, application deployment)
   - Set up PostgreSQL database
   - Configure Python environment
   - Deploy application code
   - Set up systemd service

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS/RHEL-based systems.
2. Self-signed certificates are acceptable for the migrated solution (production would likely require proper certificates).
3. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
4. The current security settings (fail2ban, ufw, SSH hardening) should be maintained in the Ansible implementation.
5. The Vagrant development environment should be preserved for testing the Ansible migration.
6. The current Redis and PostgreSQL passwords are for development only and will be replaced with proper secret management in production.
7. The directory structure for web content (/var/www/[site]) should be maintained.