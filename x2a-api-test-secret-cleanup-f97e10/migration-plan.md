# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The repository has a moderate number of cookbooks with clear responsibilities
- External dependencies on community cookbooks need to be replaced with Ansible equivalents
- Security configurations need careful migration
- Secrets management needs to be implemented in Ansible Vault

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and site configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening with fail2ban and UFW

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies - will be replaced by Ansible Galaxy requirements.yml
- `Vagrantfile`: Defines development VM - can be adapted for Ansible testing with minimal changes
- `solo.json`: Contains Chef run list and node attributes - will be converted to Ansible inventory variables
- `solo.rb`: Chef configuration - will be replaced by ansible.cfg
- `vagrant-provision.sh`: Provisioning script - will be replaced by Ansible playbook calls

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or local development environment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or direct package installation and configuration
- **memcached (~> 6.0)**: Replace with Ansible memcached role or direct package installation and configuration
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or direct package installation and configuration

### Security Considerations

- **SSL Certificate Management**: 
  - Current implementation generates self-signed certificates
  - Migration approach: Use Ansible's openssl_* modules or community.crypto collection

- **Firewall Configuration**: 
  - Current implementation uses UFW
  - Migration approach: Use Ansible's ufw module or firewalld for Fedora

- **Fail2ban Configuration**: 
  - Current implementation installs and configures fail2ban
  - Migration approach: Use Ansible's template module to configure fail2ban

- **SSH Hardening**: 
  - Current implementation disables root login and password authentication
  - Migration approach: Use Ansible's lineinfile or template module to configure SSH

- **Vault/secrets management**:
  - Redis password in cache cookbook: 'redis_secure_password_123'
  - PostgreSQL credentials in fastapi-tutorial cookbook: 'fastapi_password'
  - Database connection string in .env file
  - Migration approach: Store these secrets in Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current implementation uses Chef templates and attributes to configure multiple Nginx sites
  - Mitigation: Create Ansible templates with similar structure, use Ansible's with_items to iterate through site configurations

- **Redis Configuration Hack**: 
  - Description: The cache cookbook includes a ruby_block to modify Redis configuration file after installation
  - Mitigation: Create a custom Redis configuration template in Ansible that doesn't require post-installation modification

- **Service Dependencies**: 
  - Description: The FastAPI application depends on PostgreSQL being configured first
  - Mitigation: Use Ansible's handlers and notify mechanism to ensure proper service ordering

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Start with basic Nginx installation and configuration
   - Add SSL certificate generation
   - Add security hardening (fail2ban, UFW)
   - Add multi-site configuration

2. **cache** (low complexity, independent service)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Implement PostgreSQL installation and configuration
   - Implement Python environment setup
   - Implement application deployment from Git
   - Configure systemd service

### Assumptions

1. The target environment will continue to be Fedora-based systems
2. Self-signed certificates are acceptable for the migrated solution (production would likely use Let's Encrypt or other CA)
3. The current security configurations (fail2ban, UFW, SSH hardening) are appropriate for the target environment
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current Redis and Memcached configurations are sufficient for the application's needs
6. The PostgreSQL database schema is managed by the FastAPI application and doesn't require additional migration steps
7. The current Vagrant setup is primarily for development/testing and not production deployment