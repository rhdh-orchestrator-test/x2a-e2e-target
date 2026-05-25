# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site web application environment with caching services and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated timeline for this migration is 3-4 weeks, with medium complexity due to the multi-component architecture and security considerations.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and fail2ban integration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, firewall configuration

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file listing cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef configuration file defining the run list and node attributes including nginx site configurations and security settings
- `solo.rb`: Chef configuration file specifying cookbook paths and log settings
- `Vagrantfile`: Defines a Fedora 42 VM for development/testing with port forwarding and networking configuration
- `vagrant-provision.sh`: Shell script that installs Chef and runs the cookbooks in the Vagrant environment

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile) with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or direct package installation and configuration

### Security Considerations

- **SSL Certificate Management**: The current implementation generates self-signed certificates. Migration should maintain this capability while allowing for integration with Let's Encrypt or other certificate providers.
- **Firewall Configuration**: UFW firewall rules need to be migrated to equivalent Ansible firewall modules (ufw or firewalld depending on target OS).
- **fail2ban Integration**: Configuration needs to be migrated to Ansible tasks.
- **Security Headers**: Nginx security headers configuration needs to be preserved in templates.
- **Vault/secrets management**: 
  - Redis password in cache cookbook (hardcoded as 'redis_secure_password_123')
  - PostgreSQL database credentials in fastapi-tutorial cookbook (hardcoded as 'fastapi_password')
  - Total credentials detected: 2 hardcoded passwords

### Technical Challenges

- **Multi-site Configuration**: The dynamic generation of multiple Nginx site configurations needs to be preserved in Ansible using loops or with_items constructs.
- **SSL Certificate Generation**: Self-signed certificate generation logic needs to be replicated in Ansible.
- **Service Dependencies**: Ensuring proper ordering of service installation, configuration, and startup in Ansible.
- **Python Environment Management**: Handling Python virtual environment setup and dependency installation in Ansible.

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - First migrate the basic Nginx installation and configuration
   - Then add SSL certificate generation
   - Finally add security configurations (fail2ban, firewall)

2. **cache** (low complexity, standalone service)
   - Migrate Memcached configuration
   - Migrate Redis configuration with authentication

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Migrate PostgreSQL installation and configuration
   - Migrate Python environment setup
   - Migrate application deployment and service configuration

### Assumptions

1. The target environment will continue to be Fedora/RHEL-based systems, though the cookbooks support Ubuntu as well.
2. Self-signed certificates are acceptable for the migrated solution (production environments would likely use proper certificates).
3. The hardcoded passwords in the Chef recipes will be replaced with Ansible Vault or another secret management solution.
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
5. The current security configurations (fail2ban, UFW, SSH hardening) are appropriate for the target environment.
6. The Nginx configuration with multiple virtual hosts will be maintained in the Ansible solution.
7. The current directory structure for web content (/var/www/[site]) will be maintained.
8. The PostgreSQL database configuration for the FastAPI application will remain the same.