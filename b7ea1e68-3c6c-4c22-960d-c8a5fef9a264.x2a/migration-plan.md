# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration scope is moderate, consisting of three primary Chef cookbooks with external dependencies. Based on the complexity and size of the codebase, an estimated timeline for migration would be 2-3 weeks with 1-2 dedicated engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL setup, security hardening (fail2ban, ufw)

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

- `Berksfile`: Manages cookbook dependencies, including external cookbooks from Chef Supermarket (nginx, memcached, redisio). Will need to be replaced with Ansible Galaxy requirements.
- `solo.json`: Contains node configuration including the run list and attributes for Nginx sites and security settings. Will be migrated to Ansible inventory variables.
- `solo.rb`: Chef Solo configuration file. Will be replaced with Ansible configuration.
- `Vagrantfile`: Defines the development VM using Fedora 42. Can be adapted for Ansible-based provisioning.
- `vagrant-provision.sh`: Bash script that installs Chef and runs the cookbooks. Will be replaced with Ansible provisioning.

### Target Details

Based on the source repository analysis:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0) as indicated in cookbook metadata. The Vagrantfile uses Fedora 42.
- **Virtual Machine Technology**: Vagrant with libvirt provider (based on Vagrantfile configuration)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible `nginx` role from Galaxy or create a custom role
- **memcached (~> 6.0)**: Replace with Ansible `geerlingguy.memcached` role or equivalent
- **redisio (~> 7.2.4)**: Replace with Ansible `geerlingguy.redis` role or equivalent

### Security Considerations

- **SSL Configuration**: The nginx-multisite cookbook manages SSL certificates and private keys. Migration should maintain secure certificate handling.
  - Migration approach: Use Ansible Vault for certificate storage or integrate with external certificate management
  
- **Redis Authentication**: Redis is configured with password authentication.
  - Migration approach: Store Redis password in Ansible Vault

- **Security Hardening**: The configuration includes fail2ban, ufw firewall, and SSH hardening.
  - Migration approach: Use Ansible security roles like `dev-sec.ssh-hardening` and `dev-sec.nginx-hardening`

- **Vault/secrets management**:
  - Hardcoded credentials found in fastapi-tutorial recipe (PostgreSQL password: 'fastapi_password')
  - Hardcoded credentials found in cache recipe (Redis password: 'redis_secure_password_123')
  - These should be migrated to Ansible Vault variables

### Technical Challenges

- **Multi-site Nginx Configuration**: The nginx-multisite cookbook dynamically creates virtual hosts based on node attributes.
  - Mitigation: Create Ansible templates with Jinja2 loops to generate similar configuration from variables

- **PostgreSQL User/Database Setup**: The fastapi-tutorial cookbook uses inline shell commands for database setup.
  - Mitigation: Replace with Ansible's PostgreSQL modules for idempotent database management

- **Service Orchestration**: The current setup manages service dependencies (e.g., FastAPI depends on PostgreSQL).
  - Mitigation: Use Ansible handlers and meta dependencies to maintain proper service ordering

### Migration Order

1. **cache cookbook** (Low complexity, minimal dependencies)
   - Implement Memcached and Redis configurations
   - Address Redis authentication security

2. **nginx-multisite cookbook** (Moderate complexity)
   - Create Nginx configuration templates
   - Implement SSL certificate management
   - Configure security hardening

3. **fastapi-tutorial cookbook** (Higher complexity)
   - Set up PostgreSQL database
   - Deploy Python application
   - Configure systemd service

### Assumptions

1. The current Chef setup is functional and represents the desired end state
2. SSL certificates are managed manually (no automated Let's Encrypt integration was found)
3. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git is accessible
4. The migration will maintain the same operating system compatibility (Ubuntu 18.04+ and CentOS 7+)
5. The Vagrant development environment should be preserved with similar functionality
6. No CI/CD pipeline integration was found in the current setup, so none is planned for the Ansible migration
7. The Redis configuration contains a workaround ("fix_redis_config" ruby block) that may need special attention during migration