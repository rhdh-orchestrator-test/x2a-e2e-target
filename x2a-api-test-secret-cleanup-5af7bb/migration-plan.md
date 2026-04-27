# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies, configuration templates, and security settings. Based on the complexity and scope, this migration is estimated to require approximately 3-4 weeks with 1-2 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and self-signed certificate generation
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL/TLS setup, security hardening (fail2ban, ufw, sysctl)

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

- `Berksfile`: Dependency management file for Chef cookbooks. Lists both local and external cookbook dependencies with version constraints. Will be replaced by Ansible Galaxy requirements.yml.
- `Vagrantfile`: Defines a Fedora 42 VM for local development with port forwarding and resource allocation. Can be adapted for Ansible-based Vagrant provisioning.
- `solo.json`: Chef node attributes and run list configuration. Will be replaced by Ansible inventory variables.
- `solo.rb`: Chef Solo configuration file. Will be replaced by Ansible configuration.
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef. Will be replaced by Ansible provisioning.

### Target Details

- **Operating System**: Fedora 42 (primary) with support for Ubuntu 18.04+ and CentOS 7+ based on cookbook metadata
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role or redis_* modules

### Security Considerations

- **Firewall Configuration**: The Chef cookbook configures UFW. Migration should use Ansible's firewalld or ufw modules.
- **fail2ban Setup**: The Chef cookbook configures fail2ban. Migration should use Ansible's fail2ban_* modules.
- **SSH Hardening**: The Chef cookbook disables root login and password authentication. Migration should use Ansible's ssh_config module.
- **SSL/TLS Management**: Self-signed certificates are generated for each site. Migration should use Ansible's openssl_* modules.
- **Vault/secrets management**: 
  - Redis password is hardcoded in the cache cookbook
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook
  - These should be migrated to Ansible Vault or an external secrets management solution

### Technical Challenges

- **Multi-site Nginx Configuration**: The Chef cookbook dynamically creates site configurations based on node attributes. Ansible will need to use templates with loops to achieve the same functionality.
- **SSL Certificate Generation**: The Chef cookbook generates self-signed certificates. Ansible will need to use the openssl_* modules to replicate this functionality.
- **Service Orchestration**: The Chef cookbook manages multiple services with dependencies. Ansible will need to handle service ordering and notifications.
- **Database Initialization**: The Chef cookbook creates PostgreSQL users and databases. Ansible will need to use the postgresql_* modules to replicate this functionality.

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
   - Set up PostgreSQL database and user
   - Deploy FastAPI application from Git
   - Configure Python virtual environment and dependencies
   - Create systemd service

### Assumptions

1. The target environment will continue to be Fedora 42 or compatible Linux distributions.
2. Self-signed certificates are acceptable for the migrated solution (not using Let's Encrypt or other CA).
3. The same security hardening measures are required in the Ansible version.
4. The FastAPI application source code will remain available at the specified Git repository.
5. Redis and Memcached configurations do not require significant changes from their current setup.
6. The current directory structure in the target environment (/opt/server/*, /etc/ssl/*) should be maintained.
7. The migration does not include enhancements or feature additions beyond what's currently implemented.
8. No CI/CD pipeline integration is required as part of the migration.