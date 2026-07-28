# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server setup with FastAPI application backend and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated timeline for migration is 2-3 weeks, with moderate complexity due to the security configurations and SSL certificate management.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw)

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks. Lists both local and external cookbook dependencies with version constraints.
- `solo.json`: Chef run list and configuration data. Contains site configurations, SSL settings, and security options.
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings.
- `Vagrantfile`: Defines the development VM using Fedora 42 with libvirt provider.
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef.

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (from Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (from cookbook metadata)
- **Virtual Machine Technology**: libvirt (from Vagrantfile)
- **Cloud Platform**: Not specified, appears to be targeting on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.nginx collection
- **memcached (~> 6.0)**: Replace with Ansible memcached role or community.general.memcached module
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or community.redis collection

### Security Considerations

- **SSL Certificate Management**: Self-signed certificates are generated for each site. Migration should use Ansible's crypto modules for certificate generation.
- **Firewall Configuration**: UFW rules are configured for SSH, HTTP, and HTTPS. Use Ansible's firewalld or ufw modules.
- **Fail2ban Configuration**: Fail2ban is configured for intrusion prevention. Use Ansible's fail2ban role or modules.
- **SSH Hardening**: SSH configuration disables root login and password authentication. Use Ansible's openssh_* modules.
- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook (`fastapi`/`fastapi_password`)
  - Consider using Ansible Vault for these credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: The current setup uses Chef templates to generate site configurations. Ansible templates will need to be created with similar logic.
- **SSL Certificate Generation**: Self-signed certificates are generated for each site. Ansible's openssl_* modules will need to be used.
- **Service Dependencies**: The FastAPI application depends on PostgreSQL. Ansible handlers and wait_for modules will be needed to ensure proper service startup order.
- **Redis Configuration Hack**: There's a custom Ruby block to modify Redis configuration. This will need to be replaced with Ansible's lineinfile or template module.

### Migration Order

1. **cache** (low risk, foundational service)
   - Start with memcached and redis configuration as they are relatively simple and independent
   - Create Ansible roles for each caching service

2. **nginx-multisite** (moderate complexity)
   - Create Ansible role for Nginx installation and configuration
   - Implement security hardening (fail2ban, ufw, sysctl)
   - Set up SSL certificate generation
   - Configure virtual hosts

3. **fastapi-tutorial** (high complexity, dependencies)
   - Set up PostgreSQL database
   - Deploy Python application from Git
   - Configure virtual environment and dependencies
   - Create systemd service

### Assumptions

1. The target environment will continue to be Fedora 42 or compatible Linux distributions.
2. Self-signed certificates are acceptable for the migrated solution (not using Let's Encrypt or other CA).
3. The current security configurations (fail2ban, ufw, SSH hardening) are required in the migrated solution.
4. The PostgreSQL database will be local to the application server as in the current setup.
5. The Redis password and PostgreSQL credentials will be managed securely in the new solution.
6. The Vagrant development environment will be maintained but converted to use Ansible provisioner.
7. The current directory structure for web content (/var/www/site.cluster.local) will be maintained.