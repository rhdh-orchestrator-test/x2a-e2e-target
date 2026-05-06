# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site web application environment with caching services and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to Ansible roles and playbooks. The estimated complexity is moderate, with security configurations and multiple service integrations requiring careful attention.

**Timeline Estimate:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

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

- `Berksfile`: Manages cookbook dependencies including nginx (~> 12.0), memcached (~> 6.0), and redisio (~> 7.2.4)
- `solo.json`: Defines the run list and configuration parameters for Chef Solo
- `solo.rb`: Configures Chef Solo paths and logging
- `Vagrantfile`: Defines a Fedora 42 VM with port forwarding and networking for development
- `vagrant-provision.sh`: Bash script to install Chef and run the provisioning process

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for local development

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks
- **PostgreSQL**: Replace with Ansible postgresql_* modules or community.postgresql collection

### Security Considerations

- **SSL Certificate Management**: 
  - Current approach uses self-signed certificates generated with OpenSSL
  - Migration approach: Use ansible.builtin.openssl_* modules or community.crypto collection

- **Firewall Configuration**: 
  - Current approach uses UFW with explicit allow rules
  - Migration approach: Use ansible.posix.ufw module

- **Fail2ban Integration**: 
  - Current approach configures fail2ban with a custom jail.local template
  - Migration approach: Use community.general.fail2ban module or template tasks

- **SSH Hardening**: 
  - Current approach disables root login and password authentication
  - Migration approach: Use ansible.posix.sshd_config module

- **Vault/secrets management**:
  - Redis password hardcoded in recipe (redis_secure_password_123)
  - PostgreSQL credentials hardcoded in recipe (fastapi/fastapi_password)
  - Migration approach: Use Ansible Vault for all credentials

### Technical Challenges

- **Multi-site Configuration**: 
  - Description: The nginx-multisite cookbook dynamically creates virtual host configurations based on node attributes
  - Mitigation: Use Ansible with_items/loop constructs with templates to achieve similar functionality

- **Service Orchestration**: 
  - Description: The current setup manages dependencies between services (e.g., FastAPI depends on PostgreSQL)
  - Mitigation: Use Ansible handlers and meta dependencies to ensure proper service ordering

- **SSL Certificate Generation**: 
  - Description: Self-signed certificates are generated for each virtual host
  - Mitigation: Use the community.crypto.openssl_certificate module with proper idempotency checks

- **Configuration File Modifications**: 
  - Description: The cache cookbook uses a ruby_block to modify Redis configuration files
  - Mitigation: Use Ansible's lineinfile or template modules with proper regexp patterns

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for web services)
   - Create base nginx role
   - Implement virtual host configuration
   - Implement SSL certificate generation
   - Implement security configurations (fail2ban, ufw)

2. **cache** (low complexity, independent service)
   - Create memcached role
   - Create redis role with authentication

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Create PostgreSQL role
   - Create Python application deployment role
   - Implement systemd service configuration

### Assumptions

1. The target environment will continue to be Fedora 42 as specified in the Vagrantfile
2. Self-signed certificates are acceptable for the migrated solution (production would likely use Let's Encrypt or similar)
3. The current security configurations (fail2ban, ufw, SSH hardening) are required in the migrated solution
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current Redis and PostgreSQL passwords are development passwords and will be replaced with secure passwords in Ansible Vault
6. The nginx virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local) will remain the same
7. The current port mappings (80/443 internally, 8080/8443 forwarded) will be maintained