# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- External dependencies are explicitly defined in the Berksfile
- Security configurations are present and need careful migration
- Secrets management will need to be addressed (Redis password, PostgreSQL credentials)

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and self-signed certificates
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
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies including external cookbooks from Chef Supermarket (nginx, memcached, redisio)
- `solo.json`: Contains the run list and configuration data for Chef Solo, including Nginx site configurations and security settings
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Defines the Vagrant VM configuration (Fedora 42) with port forwarding and networking settings

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with Fedora 42 used in the Vagrant environment
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for local development/testing

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks with custom configuration

### Security Considerations

- **Firewall Configuration**: The Chef cookbook configures UFW with specific rules for SSH, HTTP, and HTTPS. This should be migrated to Ansible's `ufw` module or `firewalld` module depending on the target OS.
- **fail2ban Setup**: The cookbook configures fail2ban for intrusion prevention. This should be migrated to Ansible tasks using the `template` module for configuration files.
- **SSH Hardening**: SSH configuration includes disabling root login and password authentication. This should be migrated using Ansible's `lineinfile` or `template` modules.
- **SSL Certificate Management**: Self-signed certificates are generated for each virtual host. This should be migrated to Ansible using the `openssl_*` modules.
- **Vault/secrets management**:
  - Redis authentication password: "redis_secure_password_123" in cache/recipes/default.rb
  - PostgreSQL credentials: Username "fastapi" with password "fastapi_password" in fastapi-tutorial/recipes/default.rb
  - These should be moved to Ansible Vault or another secrets management solution

### Technical Challenges

- **Multi-site Nginx Configuration**: The Chef cookbook dynamically creates Nginx site configurations based on attributes. This will need to be replicated in Ansible using templates and loops.
- **SSL Certificate Generation**: The Chef cookbook generates self-signed certificates for each site. This will need to be implemented in Ansible using the `openssl_*` modules.
- **Service Dependencies**: The FastAPI application depends on PostgreSQL. This dependency needs to be maintained in the Ansible playbook.
- **Idempotent Database Creation**: The Chef cookbook uses shell commands for database creation. This should be replaced with Ansible's PostgreSQL modules for better idempotence.

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for web services)
   - Create base Nginx role with security hardening
   - Implement virtual host configuration with SSL support
   - Migrate security configurations (fail2ban, ufw)

2. **cache** (low complexity, independent service)
   - Create roles for Memcached and Redis
   - Implement Redis authentication
   - Ensure proper service configuration

3. **fastapi-tutorial** (high complexity, application deployment)
   - Create PostgreSQL role
   - Implement Python application deployment
   - Configure systemd service
   - Set up database and application integration

### Assumptions

1. The target environment will continue to use the same operating systems (Ubuntu/CentOS/Fedora)
2. The Vagrant development environment will be maintained
3. Self-signed certificates are acceptable for the migrated solution (vs. Let's Encrypt or other CA)
4. The FastAPI application source repository will remain available at the specified URL
5. The current security configurations are appropriate for the target environment
6. The Redis and PostgreSQL passwords in the code are development credentials and will be replaced with secure values in production
7. The current directory structure for web content and application code will be maintained