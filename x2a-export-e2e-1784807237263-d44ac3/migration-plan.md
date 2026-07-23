# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with FastAPI application and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1 week
- Documentation and Knowledge Transfer: 1 week
- Total: 5-6 weeks

**Complexity Assessment:** Medium
- Well-structured Chef cookbooks with clear separation of concerns
- Standard infrastructure components (Nginx, FastAPI, PostgreSQL, Redis, Memcached)
- Security configurations that need careful migration
- Self-signed SSL certificates management

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and self-signed certificates
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw, sysctl)

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment, Git repository deployment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies (nginx, memcached, redisio)
- `solo.json`: Defines the run list and configuration parameters for sites and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Defines the development VM (Fedora 42) with network configuration
- `vagrant-provision.sh`: Shell script to provision the VM with Chef

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or local development

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible `nginx` role or use the `ansible.builtin.package` module to install Nginx and manage configuration files with templates
- **memcached (~> 6.0)**: Replace with Ansible `memcached` role or use the `ansible.builtin.package` module with appropriate templates
- **redisio (~> 7.2.4)**: Replace with Ansible `redis` role or use the `ansible.builtin.package` module with appropriate templates

### Security Considerations

- **SSL Certificate Management**: The current implementation generates self-signed certificates. In Ansible, use the `openssl_*` modules to generate certificates.
- **Firewall Configuration**: The Chef cookbook configures UFW. In Ansible, use the `ufw` module to manage firewall rules.
- **Fail2ban Configuration**: The Chef cookbook configures fail2ban. In Ansible, use the `ansible.builtin.template` module to configure fail2ban.
- **SSH Hardening**: The Chef cookbook disables root login and password authentication. In Ansible, use the `ansible.posix.sshd` module or templates to configure SSH.
- **Vault/secrets management**:
  - Redis password in the cache cookbook (`redis_secure_password_123`)
  - PostgreSQL database credentials in the fastapi-tutorial cookbook (`fastapi:fastapi_password`)
  - These should be migrated to Ansible Vault or an external secrets management solution

### Technical Challenges

- **Multi-site Nginx Configuration**: The Chef cookbook dynamically creates Nginx site configurations based on attributes. In Ansible, this can be implemented using loops with templates.
- **SSL Certificate Generation**: The Chef cookbook generates self-signed certificates for each site. In Ansible, this can be implemented using the `openssl_certificate` module.
- **Service Dependencies**: The FastAPI application depends on PostgreSQL. In Ansible, this can be managed using handlers and the `meta: flush_handlers` directive.
- **Idempotent Database Creation**: The Chef cookbook uses PostgreSQL commands to create databases and users. In Ansible, use the `postgresql_*` modules to ensure idempotency.

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Start with basic Nginx installation and configuration
   - Add SSL certificate generation
   - Add security hardening (fail2ban, ufw, sysctl)
   - Add multi-site configuration

2. **cache** (low complexity, independent service)
   - Implement Memcached configuration
   - Implement Redis configuration with authentication

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Implement PostgreSQL installation and configuration
   - Implement Python environment setup
   - Implement application deployment
   - Implement systemd service configuration

### Assumptions

1. The target environment will continue to be Fedora 42 or a compatible Linux distribution.
2. The self-signed certificates are for development/testing only and not for production use.
3. The current security configurations (fail2ban, ufw, SSH hardening) are appropriate for the target environment.
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git is accessible and will remain available.
5. The current Redis and Memcached configurations are sufficient for the application's needs.
6. The PostgreSQL database configuration is minimal and doesn't include advanced features like replication or backups.
7. The current Chef implementation doesn't use encrypted data bags or other secret management features.