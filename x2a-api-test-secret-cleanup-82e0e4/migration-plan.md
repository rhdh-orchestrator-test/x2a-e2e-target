# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI Python application with PostgreSQL database. The migration to Ansible will involve converting three Chef cookbooks with their dependencies, configuration templates, and security settings.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 3 weeks
- Testing and Validation: 2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 7 weeks

**Complexity Assessment:** Medium
- Well-structured Chef cookbooks with clear separation of concerns
- Standard web server, caching, and application patterns
- Security configurations that need careful migration
- External cookbook dependencies that need Ansible equivalents

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and SSL certificate management
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL/TLS setup with self-signed certificates, security hardening (fail2ban, ufw, sysctl)

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, log directory management

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository deployment, Python virtual environment setup, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies including external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `Vagrantfile`: Defines development VM using Fedora 42, with port forwarding and resource allocation
- `solo.json`: Defines Chef run list and node attributes including nginx site configurations and security settings
- `solo.rb`: Chef Solo configuration file
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef

### Target Details

- **Operating System**: Fedora (based on Vagrantfile using "generic/fedora42" box)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or local development

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role (e.g., geerlingguy.nginx or custom role)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role (e.g., geerlingguy.redis or DavidWittman.redis)

### Security Considerations

- **SSL/TLS Configuration**: 
  - Migration approach: Use Ansible's openssl_* modules to generate self-signed certificates
  - Ensure proper file permissions for private keys (0640) and certificate files

- **Firewall (UFW)**: 
  - Migration approach: Use Ansible's ufw module to configure firewall rules
  - Ensure default deny policy and specific allow rules for SSH, HTTP, HTTPS

- **fail2ban**: 
  - Migration approach: Use Ansible to install and configure fail2ban
  - Migrate jail.local template to Ansible template

- **SSH Hardening**: 
  - Migration approach: Use Ansible's lineinfile or template module to configure sshd_config
  - Maintain settings for disabling root login and password authentication

- **Sysctl Security Settings**: 
  - Migration approach: Use Ansible's sysctl module to apply kernel parameters

- **Vault/secrets management**:
  - Redis password in cache cookbook: Use Ansible Vault to store the Redis password
  - PostgreSQL credentials in fastapi-tutorial cookbook: Use Ansible Vault for database credentials
  - Count of credentials detected: 2 (Redis password, PostgreSQL user/password)

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The Chef cookbook dynamically creates multiple virtual hosts with SSL
  - Mitigation: Create an Ansible role with templates that can handle multiple sites from variables

- **SSL Certificate Generation**: 
  - Description: Self-signed certificates are generated for each site
  - Mitigation: Use Ansible's openssl_* modules to generate certificates with proper idempotence checks

- **Service Dependencies**: 
  - Description: FastAPI application depends on PostgreSQL service
  - Mitigation: Use Ansible handlers and meta dependencies to ensure proper service ordering

- **Python Environment Setup**: 
  - Description: Python virtual environment creation and package installation
  - Mitigation: Use Ansible's pip module with virtualenv parameter

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Contains security configurations that should be established first

2. **cache** (Priority 2)
   - Moderate complexity with external dependencies
   - Required by the application but not as fundamental as nginx

3. **fastapi-tutorial** (Priority 3)
   - Depends on both nginx and potentially cache services
   - Most complex with database setup, git deployment, and service configuration

### Assumptions

1. The target environment will continue to be Fedora-based systems
2. Self-signed certificates are acceptable for the migrated environment
3. The same security policies should be maintained in the Ansible version
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The same directory structure for web roots and application files will be maintained
6. No additional monitoring or logging requirements beyond what's in the current Chef setup
7. The migration will not involve changes to the application code itself
8. The Vagrant development environment should be preserved with similar networking and resource allocation