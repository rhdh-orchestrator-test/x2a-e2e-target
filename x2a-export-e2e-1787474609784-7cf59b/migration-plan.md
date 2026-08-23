# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with caching services (Redis and Memcached) and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks with their recipes, templates, and attributes to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- Well-structured Chef cookbooks with clear separation of concerns
- Standard infrastructure components (Nginx, Redis, Memcached, PostgreSQL)
- Self-contained development environment using Vagrant

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw), sysctl security settings

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
- `solo.json`: Contains node attributes and run list - will be replaced by Ansible inventory variables
- `solo.rb`: Chef configuration file - not needed in Ansible
- `Vagrantfile`: Defines the development VM - can be adapted for Ansible provisioning
- `vagrant-provision.sh`: Installs Chef and runs cookbooks - will be replaced with Ansible provisioning

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role from Galaxy or create a custom role
- **memcached (~> 6.0)**: Replace with Ansible memcached role from Galaxy
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role from Galaxy

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated in the Chef cookbook
  - Migration approach: Use Ansible's openssl_* modules for certificate generation

- **Firewall Configuration**: 
  - UFW is configured in the security.rb recipe
  - Migration approach: Use Ansible's ufw module for firewall management

- **SSH Hardening**:
  - Root login disabled and password authentication disabled
  - Migration approach: Use Ansible's lineinfile module or ssh_config module

- **System Hardening**:
  - Sysctl security settings applied
  - Migration approach: Use Ansible's sysctl module

- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook
  - PostgreSQL password is hardcoded in the fastapi-tutorial cookbook
  - Migration approach: Use Ansible Vault for storing sensitive information

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The Chef cookbook dynamically creates Nginx site configurations based on node attributes
  - Mitigation: Use Ansible templates with loops to generate site configurations from variables

- **Service Dependencies**: 
  - Description: The FastAPI application depends on PostgreSQL being configured first
  - Mitigation: Use Ansible handlers and proper task ordering to ensure dependencies are met

- **SSL Certificate Generation**: 
  - Description: Self-signed certificates are generated for each site
  - Mitigation: Use Ansible's openssl_* modules with proper idempotency checks

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Start with basic Nginx configuration and site setup
   - Add SSL and security features

2. **cache** (Priority 2)
   - Relatively simple configuration with external dependencies
   - Implement Memcached and Redis configurations

3. **fastapi-tutorial** (Priority 3)
   - Application deployment with database dependencies
   - Requires PostgreSQL setup and Python environment configuration

### Assumptions

1. The target environment will continue to use Fedora as the base OS
2. Self-signed certificates are acceptable for the migrated solution
3. The same security hardening measures will be applied in the Ansible roles
4. The Vagrant development environment will be maintained
5. No changes to the application code or database schema are required
6. The current network configuration and port mappings will be preserved
7. The Redis and PostgreSQL passwords will be managed securely in the new implementation
8. The current directory structure for web content will be maintained