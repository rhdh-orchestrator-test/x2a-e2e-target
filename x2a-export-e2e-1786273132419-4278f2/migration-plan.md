# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-component web application stack. The migration scope includes three Chef cookbooks that manage:

1. A multi-site Nginx web server with SSL configuration
2. Caching services (Memcached and Redis)
3. A FastAPI Python application with PostgreSQL database

The migration complexity is **moderate** with an estimated timeline of 2-3 weeks for a single developer or 1 week for a small team. The repository has a clear structure with well-defined cookbooks and minimal external dependencies.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
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

- `Berksfile`: Dependency management file for Chef cookbooks. Lists both local and external cookbook dependencies with version constraints.
- `solo.json`: Chef configuration file containing the run list and node attributes. Defines Nginx sites, SSL paths, and security settings.
- `solo.rb`: Chef configuration file for Chef Solo execution.
- `vagrant-provision.sh`: Bash script for provisioning a Vagrant VM with Chef. Installs Chef, Berkshelf, and runs the Chef Solo provisioner.
- `Vagrantfile`: Vagrant configuration file for local development environment.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 18.04 or later / CentOS 7 or later (both supported in cookbooks)
- **Virtual Machine Technology**: VirtualBox (inferred from Vagrant usage)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible `nginx` role or `ansible.builtin.package` module + templates
- **memcached (~> 6.0)**: Replace with Ansible `memcached` role or direct package installation
- **redisio (~> 7.2.4)**: Replace with Ansible `redis` role or direct package installation

### Security Considerations

- **SSL Certificate Management**: The current implementation generates self-signed certificates. Migration should:
  - Use Ansible's `openssl_*` modules for certificate generation
  - Consider integration with Let's Encrypt via `community.crypto.acme_certificate`

- **Firewall Configuration**: Current implementation uses UFW. Migration should:
  - Use Ansible's `ufw` module or `firewalld` module depending on target OS

- **SSH Hardening**: Current implementation disables root login and password authentication. Migration should:
  - Use Ansible's `lineinfile` or `template` modules to configure SSH

- **Fail2ban Configuration**: Current implementation installs and configures fail2ban. Migration should:
  - Use Ansible's `package` and `template` modules to install and configure fail2ban

- **Vault/secrets management**: 
  - Redis password is hardcoded in the `cache` cookbook
  - PostgreSQL credentials are hardcoded in the `fastapi-tutorial` cookbook
  - Migration should use Ansible Vault for all credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: The current implementation uses Chef templates and attributes to configure multiple Nginx sites. Migration should:
  - Create Ansible templates for Nginx site configurations
  - Use Ansible variables to define site properties
  - Implement handlers for service reloads

- **Redis Configuration Hack**: The current implementation includes a Ruby block to modify Redis configuration files after installation. Migration should:
  - Use Ansible templates to generate proper Redis configuration files
  - Avoid post-installation modifications

- **PostgreSQL User and Database Creation**: The current implementation uses shell commands via `execute` resources. Migration should:
  - Use Ansible's `postgresql_*` modules for database and user management

### Migration Order

1. **cache cookbook** (low risk, straightforward package installations)
   - Implement Memcached installation and configuration
   - Implement Redis installation with authentication

2. **nginx-multisite cookbook** (moderate complexity)
   - Implement Nginx installation and base configuration
   - Implement SSL certificate generation
   - Implement security configurations (fail2ban, firewall)
   - Implement virtual host configurations

3. **fastapi-tutorial cookbook** (higher complexity, dependencies)
   - Implement PostgreSQL installation and configuration
   - Implement Python environment setup
   - Implement application deployment from Git
   - Implement systemd service configuration

### Assumptions

1. The target environment will continue to be Ubuntu/CentOS based systems
2. Self-signed certificates are acceptable for development/testing
3. The FastAPI application code repository at `https://github.com/dibanez/fastapi_tutorial.git` will remain accessible
4. The current security configurations (disabling root SSH, password authentication) are appropriate for the target environment
5. The current Redis password and PostgreSQL credentials will be migrated as-is initially, then updated according to security policies
6. The Vagrant development environment will be replaced with an equivalent Ansible-based local development solution