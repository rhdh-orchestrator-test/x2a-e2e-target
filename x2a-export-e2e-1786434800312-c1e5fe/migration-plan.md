# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with caching services and a FastAPI application. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The codebase is well-structured with clear separation of concerns
- Moderate number of external dependencies (nginx, memcached, redisio)
- Security configurations that need careful migration
- Database and application deployment that requires proper sequencing

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw, sysctl)

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

- `Berksfile`: Defines cookbook dependencies - will be replaced by Ansible Galaxy requirements.yml
- `solo.json`: Contains node attributes and run list - will be replaced by Ansible inventory variables
- `solo.rb`: Chef configuration file - will be replaced by ansible.cfg
- `Vagrantfile`: VM configuration for development/testing - can be adapted for Ansible testing
- `vagrant-provision.sh`: Provisioning script - will be replaced by Ansible playbook

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (from Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (from cookbook metadata)
- **Virtual Machine Technology**: libvirt (from Vagrantfile)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible community.general.nginx_* modules or geerlingguy.nginx role
- **memcached (~> 6.0)**: Replace with geerlingguy.memcached role
- **redisio (~> 7.2.4)**: Replace with geerlingguy.redis role or community.general.redis_* modules

### Security Considerations

- **Firewall Configuration**: The Chef cookbook configures UFW. Migrate to Ansible's ansible.posix.ufw module
- **Fail2ban Setup**: Migrate fail2ban configuration to ansible.posix.fail2ban module
- **SSH Hardening**: Migrate SSH security settings using ansible.posix.ssh_config module
- **SSL Certificate Management**: Replace self-signed certificate generation with ansible.builtin.openssl_* modules
- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook ('redis_secure_password_123')
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook ('fastapi'/'fastapi_password')
  - Consider using Ansible Vault for these credentials

### Technical Challenges

- **Multi-site Configuration**: The nginx-multisite cookbook dynamically creates site configurations based on node attributes. This pattern needs to be replicated in Ansible using templates and loops.
- **Service Dependencies**: The FastAPI application depends on PostgreSQL. Ensure proper sequencing in Ansible playbooks.
- **SSL Certificate Management**: Self-signed certificates are generated for development. Ensure proper handling in Ansible, potentially with ansible.builtin.openssl_* modules.
- **Redis Configuration Hack**: The Chef cookbook includes a ruby_block to fix Redis configuration. This will need a custom approach in Ansible.

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Start with basic Nginx installation and configuration
   - Add SSL certificate management
   - Add security hardening (fail2ban, ufw, sysctl)
   - Add virtual host configuration

2. **cache** (Priority 2)
   - Memcached and Redis services
   - Ensure Redis authentication is properly secured with Ansible Vault

3. **fastapi-tutorial** (Priority 3)
   - PostgreSQL database setup
   - Python application deployment
   - Service configuration

### Assumptions

1. The target environment will continue to use Fedora 42 or similar Linux distributions.
2. The same network configuration (ports, IPs) will be maintained.
3. Self-signed certificates are acceptable for the migrated solution (production would likely use Let's Encrypt or other CA).
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
5. The current security settings (fail2ban, ufw, SSH hardening) are appropriate for the target environment.
6. Redis and PostgreSQL passwords will be managed securely in the new Ansible implementation.
7. The same directory structure for web content and application code will be maintained.