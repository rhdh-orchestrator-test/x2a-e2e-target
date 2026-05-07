# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI application with PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks, handling external dependencies, and ensuring proper security configurations are maintained.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 3-4 weeks
- Testing and Validation: 2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 7-8 weeks

**Complexity Assessment:**
- Medium complexity due to multiple services and security configurations
- Straightforward conversion patterns with well-defined Chef cookbooks
- No custom resources or complex Chef-specific patterns identified

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and self-signed certificate generation
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL/TLS setup, security hardening (fail2ban, UFW firewall)

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

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef Solo configuration file with run list and node attributes
- `solo.rb`: Chef Solo configuration file with file paths and log settings
- `vagrant-provision.sh`: Bash script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Vagrant configuration file for local development environment using Fedora 42

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0) as specified in cookbook metadata, but the Vagrantfile uses Fedora 42
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` module and templates
- **memcached (~> 6.0)**: Replace with Ansible's `memcached` module
- **redisio (~> 7.2.4)**: Replace with Ansible's `redis` module and templates
- **PostgreSQL**: Use Ansible's `postgresql` modules for database and user management

### Security Considerations

- **Firewall Configuration**: 
  - Migration approach: Use Ansible's `ufw` module to configure firewall rules
  - Ensure SSH, HTTP, and HTTPS ports remain accessible

- **Fail2ban Setup**: 
  - Migration approach: Use Ansible to install and configure fail2ban
  - Maintain existing jail configurations

- **SSH Hardening**: 
  - Migration approach: Use Ansible to configure SSH daemon settings
  - Maintain root login restrictions and password authentication settings

- **SSL/TLS Configuration**: 
  - Migration approach: Use Ansible's `openssl_*` modules for certificate generation
  - Maintain proper file permissions for private keys

- **Vault/secrets management**:
  - Redis password in cache cookbook (hardcoded as 'redis_secure_password_123')
  - PostgreSQL user password in fastapi-tutorial cookbook (hardcoded as 'fastapi_password')
  - Consider using Ansible Vault for these credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current setup dynamically generates Nginx site configurations based on node attributes
  - Mitigation: Use Ansible templates with loops to generate site configurations from variables

- **Self-signed Certificate Generation**: 
  - Description: The current setup generates self-signed certificates for each site
  - Mitigation: Use Ansible's `openssl_certificate` module to generate certificates

- **Redis Configuration Hacks**: 
  - Description: The current setup includes a ruby_block to modify Redis configuration files after they're created
  - Mitigation: Create proper Redis configuration templates in Ansible to avoid post-configuration modifications

- **FastAPI Application Deployment**: 
  - Description: The current setup clones a Git repository and sets up a Python environment
  - Mitigation: Use Ansible's `git` module and Python modules to handle deployment

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Start with basic Nginx installation and configuration
   - Add SSL/TLS certificate generation
   - Configure virtual hosts
   - Implement security hardening

2. **cache** (low complexity, independent service)
   - Set up Memcached
   - Configure Redis with authentication

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Set up PostgreSQL
   - Deploy FastAPI application
   - Configure systemd service

### Assumptions

1. The target environment will continue to be Fedora-based (as indicated by the Vagrantfile)
2. Self-signed certificates are acceptable for development/testing (production would likely use proper certificates)
3. The security configurations (fail2ban, UFW, SSH hardening) are required in the target environment
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current hardcoded passwords in the Chef recipes are for development only and will be replaced with proper secret management in Ansible
6. The current directory structure in the target environment (/opt/fastapi-tutorial, /var/www/sites) will be maintained
7. The Vagrant setup is primarily for development/testing and may not be required in the final Ansible configuration