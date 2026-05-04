# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site web application environment with caching services and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated timeline for this migration is 3-4 weeks, with moderate complexity due to the security configurations and multi-site setup.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, fail2ban integration, UFW firewall configuration

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

- `Berksfile`: Dependency management file listing cookbook dependencies (nginx, memcached, redisio)
- `solo.json`: Chef configuration file defining the run list and node attributes
- `solo.rb`: Chef configuration file defining paths and log settings
- `Vagrantfile`: Defines a Fedora 42 VM for development/testing with port forwarding and resource allocation
- `vagrant-provision.sh`: Shell script that installs Chef and runs the cookbooks in the Vagrant environment

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or nginx_core module
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks
- **PostgreSQL**: Replace with Ansible postgresql role or postgresql_* modules

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for each site
  - Migration should use Ansible's openssl_* modules for certificate generation
  - Consider integrating with Let's Encrypt for production environments

- **Firewall Configuration**: 
  - UFW is configured with specific rules for SSH, HTTP, and HTTPS
  - Migration should use Ansible's ufw module or firewalld module depending on target OS

- **System Hardening**:
  - Sysctl security parameters are configured
  - SSH hardening (root login disabled, password authentication disabled)
  - Migration should use Ansible's sysctl module and template module for SSH configuration

- **Fail2ban Integration**:
  - Fail2ban is configured for brute force protection
  - Migration should use Ansible's template module for fail2ban configuration

- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook
  - PostgreSQL password is hardcoded in the fastapi-tutorial cookbook
  - Migration should use Ansible Vault for storing sensitive credentials

### Technical Challenges

- **Multi-site Configuration**: 
  - The nginx-multisite cookbook dynamically creates site configurations based on node attributes
  - Migration should use Ansible loops with templates to achieve similar functionality
  - Challenge: Ensuring proper template variable substitution and maintaining the same level of flexibility

- **SSL Certificate Generation**:
  - Self-signed certificates are generated with specific parameters
  - Challenge: Ensuring certificates are only generated when needed (idempotency)

- **Service Dependencies**:
  - FastAPI application depends on PostgreSQL service
  - Challenge: Ensuring proper service ordering and dependency management in Ansible

- **Configuration File Modifications**:
  - Redis configuration has custom modifications via a ruby_block
  - Challenge: Implementing equivalent functionality in Ansible (may require lineinfile or template with conditionals)

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for web services)
   - Start with basic Nginx installation and configuration
   - Add SSL certificate generation
   - Implement security configurations (fail2ban, UFW, security headers)
   - Configure multi-site virtual hosts

2. **cache** (low complexity, standalone services)
   - Implement Memcached configuration
   - Implement Redis with authentication
   - Ensure proper service management

3. **fastapi-tutorial** (high complexity, application deployment)
   - Set up PostgreSQL database and user
   - Configure Python environment and dependencies
   - Deploy application code from Git
   - Create systemd service configuration

### Assumptions

1. The target environment will continue to be Fedora/RHEL-based or Ubuntu/Debian-based systems
2. Self-signed certificates are acceptable for development, but production may require proper CA-signed certificates
3. The current security configurations are appropriate and should be maintained in the Ansible implementation
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current Redis and PostgreSQL password practices are acceptable, though they should be moved to Ansible Vault
6. The current directory structure in the target environment (/opt/fastapi-tutorial, /var/www/sites) will be maintained
7. The Vagrant development environment will be replaced with an equivalent Ansible-based setup