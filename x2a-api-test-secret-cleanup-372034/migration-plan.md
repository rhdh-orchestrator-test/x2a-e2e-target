# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI application with PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies, configuration templates, and security settings. Based on the complexity and interdependencies, this migration is estimated to be of medium complexity and should take approximately 2-3 weeks for a skilled Ansible developer.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and custom site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, UFW firewall), sysctl security settings

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies with version constraints
- `solo.json`: Chef configuration file containing the run list and node attributes for Nginx sites and security settings
- `solo.rb`: Chef configuration file specifying cookbook paths and log settings
- `Vagrantfile`: Defines a Fedora 42 VM for local development and testing
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef

### Target Details

Based on the source repository analysis:

- **Operating System**: The configuration supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), but the Vagrantfile specifies Fedora 42 as the development environment
- **Virtual Machine Technology**: Vagrant with libvirt provider (based on Vagrantfile configuration)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks
- **Python 3 and pip**: Use Ansible's package module and pip module for Python dependency management
- **PostgreSQL**: Use Ansible's postgresql_* modules from the community.postgresql collection

### Security Considerations

- **Firewall Configuration**: The Chef cookbook configures UFW firewall rules that need to be migrated to Ansible's ufw module
- **fail2ban**: Configuration needs to be migrated to Ansible tasks using the fail2ban module
- **SSH Hardening**: SSH configuration (disabling root login, password authentication) needs to be migrated to Ansible's template or lineinfile modules
- **sysctl Security Settings**: System kernel parameters need to be migrated to Ansible's sysctl module
- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook (`redis_secure_password_123`)
  - PostgreSQL database credentials are hardcoded in the fastapi-tutorial cookbook (`fastapi:fastapi_password`)
  - SSL certificates are generated on the fly with self-signed certificates
  - Total credentials detected: 2 (Redis password, PostgreSQL password)

### Technical Challenges

- **Custom Resource Migration**: The `lineinfile` custom resource in the nginx-multisite cookbook needs to be replaced with Ansible's native lineinfile module
- **SSL Certificate Generation**: Self-signed certificate generation logic needs to be migrated to Ansible's openssl_* modules
- **Ruby Block Conversion**: Ruby blocks in the cache cookbook for fixing Redis configuration need to be converted to Ansible's lineinfile or template modules
- **Multi-site Configuration**: The dynamic generation of Nginx site configurations based on node attributes needs to be converted to Ansible loops with templates

### Migration Order

1. **nginx-multisite** (Priority 1): Core infrastructure component that other services depend on
   - First migrate the basic Nginx installation and configuration
   - Then migrate the SSL certificate generation
   - Finally migrate the security hardening features

2. **cache** (Priority 2): Secondary services that the application may depend on
   - Migrate Memcached configuration
   - Migrate Redis configuration with authentication

3. **fastapi-tutorial** (Priority 3): Application layer that depends on the infrastructure
   - Migrate PostgreSQL database setup
   - Migrate Python environment and application deployment
   - Migrate systemd service configuration

### Assumptions

1. The target environment will continue to support either Ubuntu (>= 18.04) or CentOS (>= 7.0) as specified in the cookbook metadata
2. The Vagrant development environment using Fedora 42 will be maintained
3. Self-signed SSL certificates are acceptable for the migrated solution (production would likely use Let's Encrypt or other CA)
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The hardcoded credentials in the cookbooks will be replaced with Ansible Vault or another secret management solution
6. The current security configurations (fail2ban, UFW, SSH hardening) are appropriate for the target environment
7. The multi-site Nginx configuration with three virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local) will be maintained