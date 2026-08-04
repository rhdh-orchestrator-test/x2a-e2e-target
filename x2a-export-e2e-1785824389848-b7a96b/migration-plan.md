# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with FastAPI application and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated timeline for migration is 2-3 weeks, with moderate complexity due to the interdependencies between components and security configurations.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and self-signed certificates
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening with fail2ban and UFW

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef configuration file with run list and node attributes
- `solo.rb`: Chef configuration file for Chef Solo
- `Vagrantfile`: Defines development VM using Fedora 42, with port forwarding and network configuration
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (from Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (from cookbook metadata)
- **Virtual Machine Technology**: Libvirt (specified in Vagrantfile)
- **Cloud Platform**: Not specified, appears to be designed for on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or nginx_core module
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package module
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package module with custom configuration

### Security Considerations

- **SSL/TLS Management**: 
  - Self-signed certificates are generated for each virtual host
  - Migration should maintain the same certificate generation logic or integrate with Ansible crypto modules
  - Certificate and key paths need to be maintained: `/etc/ssl/certs` and `/etc/ssl/private`

- **Firewall Configuration**:
  - UFW is configured to allow only SSH, HTTP, and HTTPS
  - Migration should use Ansible's ufw module or firewalld for Fedora

- **SSH Hardening**:
  - Root login is disabled
  - Password authentication is disabled
  - These settings should be maintained in the Ansible playbooks

- **System Hardening**:
  - fail2ban is configured for intrusion prevention
  - Custom sysctl settings are applied via template
  - Migration should use Ansible's sysctl and fail2ban modules

- **Vault/secrets management**:
  - Redis password is hardcoded in the recipe: "redis_secure_password_123"
  - PostgreSQL credentials are hardcoded in the FastAPI recipe: "fastapi:fastapi_password"
  - These should be moved to Ansible Vault or another secrets management solution

### Technical Challenges

- **Multi-site Configuration**: The nginx-multisite cookbook manages multiple virtual hosts with different document roots and SSL configurations. This will require careful translation to Ansible templates.

- **Service Interdependencies**: The FastAPI application depends on PostgreSQL, and the nginx configuration depends on the SSL certificates. These dependencies need to be maintained in the Ansible playbook ordering.

- **Configuration Templates**: Several configuration templates are used (nginx.conf.erb, security.conf.erb, etc.) which will need to be converted to Jinja2 templates for Ansible.

- **Dynamic Site Configuration**: The nginx sites are dynamically generated from node attributes. This pattern needs to be replicated using Ansible variables.

### Migration Order

1. **cache role** (Low complexity)
   - Simple configuration of Memcached and Redis services
   - Good starting point with minimal dependencies

2. **nginx-multisite role** (Medium complexity)
   - Core web server configuration
   - Security hardening components
   - SSL certificate generation

3. **fastapi-tutorial role** (High complexity)
   - Application deployment with database dependencies
   - System service configuration
   - Environment configuration

### Assumptions

1. The target environment will continue to be Fedora-based, though the cookbooks support Ubuntu and CentOS as well.
2. The self-signed certificates approach is acceptable for the migrated solution, rather than integrating with Let's Encrypt or another CA.
3. The current security hardening measures are sufficient and should be maintained in the Ansible roles.
4. The current directory structure for web content (/var/www/[site]) will be maintained.
5. The PostgreSQL and Redis passwords currently hardcoded will be moved to Ansible Vault in the migrated solution.
6. The Vagrant development environment will be maintained but updated to use Ansible provisioning instead of Chef.