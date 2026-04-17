# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure for deploying and configuring a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application with PostgreSQL. The migration to Ansible is estimated to be of moderate complexity, with an estimated timeline of 3-4 weeks for a complete migration, including testing and documentation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, UFW), sysctl security settings

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

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `Policyfile.rb`: Chef Policyfile defining the run list and cookbook dependencies
- `Policyfile.lock.json`: Locked versions of cookbook dependencies
- `solo.json`: Configuration data for Chef Solo, contains site configurations and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Defines a Fedora 42 VM for development/testing with port forwarding
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile) with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile configuration)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or collection (e.g., `ansible.posix.nginx`)
- **ssl_certificate (~> 2.1)**: Replace with Ansible's `openssl_*` modules for certificate management
- **memcached (~> 6.0)**: Replace with Ansible memcached role or direct package installation
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role or direct package installation with configuration templates

### Security Considerations

- **Firewall Configuration**: The Chef cookbook configures UFW. Migration should use Ansible's `ansible.posix.firewalld` or `community.general.ufw` modules.
- **fail2ban**: The Chef cookbook configures fail2ban. Migration should use Ansible's `community.general.fail2ban` module.
- **SSH Hardening**: The Chef cookbook disables root login and password authentication. Migration should use Ansible's `ansible.posix.sshd` module.
- **SSL/TLS Configuration**: The Chef cookbook generates self-signed certificates. Migration should use Ansible's `openssl_*` modules.
- **Vault/secrets management**:
  - Redis password in `cache/recipes/default.rb` (hardcoded as 'redis_secure_password_123')
  - PostgreSQL password in `fastapi-tutorial/recipes/default.rb` (hardcoded as 'fastapi_password')
  - Environment variables in `.env` file for FastAPI application
  - Total credentials detected: 2 hardcoded passwords

### Technical Challenges

- **Multi-site Nginx Configuration**: The Chef cookbook uses templates to generate site configurations. Migration should use Ansible templates with similar variables.
- **SSL Certificate Generation**: The Chef cookbook generates self-signed certificates. Migration should use Ansible's `openssl_*` modules with similar parameters.
- **PostgreSQL User/Database Creation**: The Chef cookbook uses shell commands. Migration should use Ansible's `community.postgresql` collection.
- **Python Virtual Environment**: The Chef cookbook creates and configures a Python virtual environment. Migration should use Ansible's `pip` module with the `virtualenv` parameter.

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Start with basic Nginx installation and configuration
   - Add SSL certificate generation
   - Add security hardening (fail2ban, UFW)
   - Add multi-site configuration

2. **cache** (low complexity, independent service)
   - Implement Memcached configuration
   - Implement Redis configuration with authentication

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Implement PostgreSQL installation and configuration
   - Implement Python environment setup
   - Implement application deployment from Git
   - Implement systemd service configuration

### Assumptions

1. The target environment will continue to be Fedora 42 or compatible Linux distributions.
2. Self-signed certificates are acceptable for the migrated solution (production would likely use Let's Encrypt or other CA).
3. The hardcoded passwords in the Chef recipes will be replaced with Ansible Vault or another secure secret management solution.
4. The directory structure for web content and application files will remain the same.
5. The Vagrant development environment will be maintained but converted to use Ansible provisioning instead of Chef.
6. No changes to the application code or database schema are required as part of the migration.
7. The current security settings (fail2ban, UFW, SSH hardening) are appropriate and should be maintained.
8. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.