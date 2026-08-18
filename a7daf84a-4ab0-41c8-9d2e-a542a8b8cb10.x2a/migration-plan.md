# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure for deploying a multi-site Nginx web server with SSL, security hardening, caching services (Redis and Memcached), and a FastAPI Python application with PostgreSQL backend. The migration to Ansible will involve converting 3 Chef cookbooks with their recipes, templates, and resources to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- No custom resources or complex Chef-specific patterns
- Standard infrastructure components (web server, database, caching)
- Security configurations that need careful migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening (fail2ban, ufw firewall), and SSL certificate management
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening with fail2ban and ufw

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

- `Berksfile`: Defines cookbook dependencies (both local and from Chef Supermarket). Will be replaced by Ansible Galaxy requirements.yml.
- `solo.json`: Contains the Chef run list and configuration attributes. Will be replaced by Ansible inventory variables.
- `solo.rb`: Chef configuration file. No direct Ansible equivalent needed.
- `Vagrantfile`: Defines the development VM. Can be adapted for Ansible with minimal changes.
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef. Will be replaced with Ansible provisioner.

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (from Vagrantfile)
- **Virtual Machine Technology**: Libvirt (from Vagrantfile)
- **Cloud Platform**: Not specified, appears to be targeting on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or direct package installation
- **memcached (~> 6.0)**: Replace with Ansible memcached role or direct package installation
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or direct package installation

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated in the nginx-multisite cookbook
  - Migration should maintain the same level of security or improve it
  - Consider using Ansible's crypto modules for certificate generation

- **Firewall Configuration**: 
  - UFW firewall is configured in the security.rb recipe
  - Migrate to Ansible's firewall modules

- **Fail2ban Configuration**:
  - Configured in security.rb recipe
  - Migrate to Ansible fail2ban role or direct configuration

- **SSH Hardening**:
  - SSH configuration hardening in security.rb
  - Migrate to Ansible's openssh_* modules

- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook: "redis_secure_password_123"
  - PostgreSQL password is hardcoded in the fastapi-tutorial cookbook: "fastapi_password"
  - These should be migrated to Ansible Vault or another secrets management solution

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - The nginx-multisite cookbook dynamically creates site configurations based on node attributes
  - Ansible solution will need to maintain this flexibility using templates and variables

- **SSL Certificate Generation**:
  - Self-signed certificates are generated for each site
  - Ansible will need to replicate this functionality using the openssl_* modules

- **Service Dependencies**:
  - The FastAPI application depends on PostgreSQL
  - Ensure proper service ordering in Ansible playbooks

- **Configuration File Management**:
  - Several configuration files are managed with templates
  - Ensure all templates are properly migrated to Ansible Jinja2 format

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Start with basic Nginx installation and configuration
   - Then add SSL and security features
   - Finally, implement multi-site configuration

2. **cache** (Priority 2)
   - Relatively independent service
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (Priority 3)
   - Application deployment that depends on other services
   - Implement PostgreSQL database setup
   - Implement Python application deployment
   - Configure systemd service

### Assumptions

1. The target environment will continue to be Fedora 42 as specified in the Vagrantfile.
2. The same network configuration (IP addresses, port forwarding) will be maintained.
3. Self-signed certificates are acceptable for the migrated solution (production would likely use Let's Encrypt or similar).
4. The FastAPI application source code will remain available at the same Git repository.
5. The current security configurations (fail2ban, ufw, SSH hardening) are appropriate for the target environment.
6. Redis and Memcached configurations do not require significant changes beyond what's currently implemented.
7. The PostgreSQL database schema is managed by the FastAPI application and doesn't require additional migration steps.