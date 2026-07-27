# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backend. The migration to Ansible will involve converting 3 Chef cookbooks with their recipes, templates, and resources to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- No complex custom resources or libraries
- Standard infrastructure components (web server, caching, application deployment)
- Security configurations that need careful migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw firewall)

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

- `Berksfile`: Defines cookbook dependencies (nginx, memcached, redisio) - will be replaced by Ansible Galaxy requirements.yml
- `solo.json`: Contains node configuration and attributes - will be converted to Ansible group_vars or host_vars
- `solo.rb`: Chef configuration file - not needed in Ansible
- `Vagrantfile`: Defines the development VM - will need updates to use Ansible provisioner instead of Chef
- `vagrant-provision.sh`: Shell script for Chef provisioning - will be replaced by Ansible playbook calls

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (from Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (from cookbook metadata)
- **Virtual Machine Technology**: Libvirt (from Vagrantfile)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible community.nginx collection or builtin nginx modules
- **memcached (~> 6.0)**: Replace with Ansible community.general.memcached module
- **redisio (~> 7.2.4)**: Replace with Ansible community.redis collection

### Security Considerations

- **Firewall Configuration**: The Chef recipes configure UFW firewall rules that need to be migrated to Ansible's ufw module
- **fail2ban**: Configuration needs to be migrated to use Ansible's fail2ban module
- **SSH Hardening**: SSH configuration (disabling root login, password authentication) needs to be migrated
- **SSL Certificates**: Self-signed certificate generation needs to be migrated to Ansible's openssl_* modules
- **Vault/secrets management**:
  - Redis password in cache cookbook (hardcoded as 'redis_secure_password_123')
  - PostgreSQL database credentials in fastapi-tutorial cookbook (hardcoded as 'fastapi_password')
  - These should be migrated to Ansible Vault or another secrets management solution

### Technical Challenges

- **Multi-site Configuration**: The dynamic generation of multiple Nginx sites based on node attributes needs careful migration to Ansible's template system and variable structure
- **Service Dependencies**: Ensuring proper ordering of service installations and configurations (e.g., PostgreSQL before FastAPI application)
- **SSL Certificate Management**: Migrating the self-signed certificate generation to Ansible's OpenSSL modules
- **Idempotency**: Ensuring all operations remain idempotent, particularly the database user creation and SSL certificate generation

### Migration Order

1. **nginx-multisite** (Priority 1): Core infrastructure component that other services depend on
   - Start with basic Nginx installation and configuration
   - Add SSL certificate management
   - Add virtual host configuration
   - Add security hardening (fail2ban, firewall)

2. **cache** (Priority 2): Supporting services
   - Memcached configuration
   - Redis installation and security configuration

3. **fastapi-tutorial** (Priority 3): Application layer
   - PostgreSQL database setup
   - Python environment configuration
   - Application deployment
   - Service configuration

### Assumptions

1. The target environment will continue to use Fedora or similar Linux distributions
2. Self-signed certificates are acceptable for development/testing (production would likely use Let's Encrypt or other CA)
3. The current security configurations (fail2ban, ufw, SSH hardening) are appropriate for the target environment
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current Redis and PostgreSQL password practices (hardcoded in recipes) will be replaced with more secure practices in Ansible
6. The Vagrant development environment will be maintained for testing
7. No custom Chef libraries or complex custom resources are in use beyond what has been discovered
8. No external Chef data bags or environments are in use