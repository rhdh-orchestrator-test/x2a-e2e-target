# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies, configuration templates, and security settings. Based on the complexity and scope, this migration is estimated to require 2-3 weeks of development time with an additional 1 week for testing and validation.

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
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file listing cookbook dependencies (nginx, memcached, redisio) - will be replaced by Ansible Galaxy requirements.yml
- `Vagrantfile`: Defines development VM configuration - can be adapted for Ansible testing with minimal changes
- `solo.json`: Contains Chef node attributes and run list - will be converted to Ansible group_vars or host_vars
- `solo.rb`: Chef configuration file - not needed in Ansible
- `vagrant-provision.sh`: Bash script for provisioning the Vagrant VM - will be replaced by Ansible playbook

### Target Details

- **Operating System**: The repository targets both Ubuntu (>= 18.04) and CentOS (>= 7.0) as specified in cookbook metadata files, with Fedora 42 used in the Vagrant development environment.
- **Virtual Machine Technology**: Libvirt is used for virtualization as specified in the Vagrantfile.
- **Cloud Platform**: No specific cloud platform is targeted; the setup appears to be designed for on-premises or generic cloud VMs.

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role from Galaxy or create custom role using nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or use package/service/template modules
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or create custom role using package/service/template modules
- **PostgreSQL**: Replace with Ansible postgresql_* modules or community.postgresql collection

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated in the nginx-multisite cookbook
  - Migration approach: Use Ansible's openssl_* modules to generate certificates or community.crypto collection

- **Firewall Configuration**: 
  - UFW is configured in the security.rb recipe
  - Migration approach: Use Ansible's ufw module to configure firewall rules

- **Fail2ban Integration**: 
  - Fail2ban is configured in the security.rb recipe
  - Migration approach: Use Ansible to deploy fail2ban configuration templates

- **SSH Hardening**: 
  - Root login and password authentication are disabled
  - Migration approach: Use Ansible's lineinfile module or ssh_config module from community.general collection

- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook (redis_secure_password_123)
  - PostgreSQL password is hardcoded in the fastapi-tutorial cookbook (fastapi_password)
  - Migration approach: Use Ansible Vault to encrypt sensitive values and store them securely

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current setup dynamically generates Nginx site configurations based on node attributes
  - Mitigation: Use Ansible templates with loops to generate site configurations from variables

- **SSL Certificate Generation**: 
  - Description: Self-signed certificates are generated for each site
  - Mitigation: Use Ansible's openssl_* modules to generate certificates with proper idempotence checks

- **Service Dependencies**: 
  - Description: The FastAPI application depends on PostgreSQL being configured first
  - Mitigation: Use Ansible handlers and proper task ordering to ensure dependencies are met

- **Redis Configuration Hacks**: 
  - Description: The cache cookbook includes a ruby_block to modify Redis configuration files after deployment
  - Mitigation: Create proper Ansible templates for Redis configuration instead of modifying files after deployment

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for web services)
   - Start with basic Nginx installation and configuration
   - Add SSL certificate generation
   - Implement security hardening (fail2ban, firewall)
   - Configure virtual hosts

2. **cache** (low complexity, independent service)
   - Implement Memcached configuration
   - Implement Redis with authentication
   - Ensure proper service management

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Set up PostgreSQL database and user
   - Deploy Python application from Git
   - Configure virtual environment and dependencies
   - Create and enable systemd service

### Assumptions

1. The target environment will continue to be Linux-based (Ubuntu/CentOS/Fedora) as specified in the cookbook metadata.
2. The same directory structure for web content (/var/www/[site]) will be maintained.
3. Self-signed certificates are acceptable for the migrated solution (production would likely use Let's Encrypt or other CA).
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
5. The current security configurations (fail2ban, UFW, SSH hardening) are appropriate for the target environment.
6. The Redis and Memcached configurations do not require advanced tuning beyond what's in the current cookbooks.
7. The Vagrant development environment will be maintained for testing the Ansible playbooks.
8. No custom Chef resources are used that would require special handling in Ansible.