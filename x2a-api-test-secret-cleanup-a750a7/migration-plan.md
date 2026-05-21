# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup with three primary cookbooks: nginx-multisite, cache, and fastapi-tutorial. The infrastructure appears to be designed for a multi-site web server environment with caching services and a FastAPI application backend. The migration to Ansible is estimated to be of moderate complexity, with an estimated timeline of 3-4 weeks for a complete migration, including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw), custom Nginx configurations

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, service management

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks. Lists both local and external cookbook dependencies with version constraints.
- `solo.json`: Chef Solo configuration file defining the run list and node attributes for Nginx sites and security settings.
- `solo.rb`: Chef Solo configuration file specifying file paths and log settings.
- `Vagrantfile`: Defines a Vagrant VM configuration using Fedora 42 with port forwarding and resource allocation.
- `vagrant-provision.sh`: Shell script that installs Chef and Berkshelf, then runs Chef Solo provisioning.

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be designed for local development/testing with Vagrant

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks with custom configuration

### Security Considerations

- **Firewall Configuration**: The Chef cookbook configures UFW. Migration should use Ansible's firewalld or ufw modules.
- **Fail2ban Setup**: Currently configured in the nginx-multisite cookbook. Use Ansible's fail2ban modules or templates.
- **SSH Hardening**: The cookbook disables root login and password authentication. Use Ansible's ssh_config module or templates.
- **SSL Certificate Management**: Self-signed certificates are generated. Consider using Ansible's openssl_* modules or community.crypto collection.
- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook's default.rb file
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook
  - Consider using Ansible Vault for storing these secrets

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of site configurations based on node attributes will need careful translation to Ansible variables and templates.
- **SSL Certificate Generation**: The self-signed certificate generation logic will need to be replicated using Ansible's openssl_* modules.
- **Service Dependencies**: Ensuring proper service dependencies and ordering in Ansible (e.g., PostgreSQL before FastAPI application).
- **Idempotency**: Ensuring all custom commands (especially database creation) are idempotent in Ansible.

### Migration Order

1. **cache cookbook** (low complexity, standalone services)
   - Implement Memcached configuration
   - Implement Redis configuration with authentication

2. **nginx-multisite cookbook** (moderate complexity, core infrastructure)
   - Implement base Nginx installation and configuration
   - Implement security hardening (fail2ban, ufw, sysctl)
   - Implement SSL certificate generation
   - Implement virtual host configuration

3. **fastapi-tutorial cookbook** (high complexity, application deployment)
   - Implement PostgreSQL installation and configuration
   - Implement Python environment setup
   - Implement application deployment from Git
   - Implement systemd service configuration

### Assumptions

1. The target environment will continue to be Fedora-based systems (specifically Fedora 42 as indicated in the Vagrantfile).
2. Self-signed certificates are acceptable for the migrated solution (production environments might require Let's Encrypt or other certificate authorities).
3. The current security configurations (fail2ban, ufw, SSH hardening) are sufficient and should be maintained in the Ansible solution.
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available and compatible.
5. The Redis configuration hack in the cache cookbook is addressing a compatibility issue that may need special handling in Ansible.
6. The current approach of storing credentials in plaintext will be replaced with Ansible Vault or another secure method.
7. The Vagrant development environment will be maintained, but Chef-specific provisioning will be replaced with Ansible.