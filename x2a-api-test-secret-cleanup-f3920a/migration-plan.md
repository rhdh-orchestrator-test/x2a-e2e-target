# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site web application environment with caching services and a FastAPI application. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated timeline for this migration is 3-4 weeks, with moderate complexity due to the interdependencies between services and security configurations.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, UFW firewall)

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

- `Berksfile`: Dependency management file for Chef cookbooks. Lists both local and external cookbook dependencies with version constraints. Will be replaced by Ansible Galaxy requirements.yml.
- `solo.json`: Chef configuration file containing the run list and node attributes. Will be replaced by Ansible inventory variables.
- `solo.rb`: Chef configuration file specifying paths and log settings. Will be replaced by Ansible configuration.
- `Vagrantfile`: Defines the development VM using Fedora 42. Can be adapted to use Ansible provisioner instead of Chef.
- `vagrant-provision.sh`: Shell script that installs Chef and runs the cookbooks. Will be replaced with Ansible provisioning script.

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (primary) with support for Ubuntu 18.04+ and CentOS 7+ as indicated in cookbook metadata
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role from Galaxy or create a custom role
- **memcached (~> 6.0)**: Replace with Ansible memcached role from Galaxy
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role from Galaxy

### Security Considerations

- **Firewall Configuration**: The Chef cookbook configures UFW. Migration should use Ansible's `ufw` or `firewalld` modules depending on target OS.
- **Fail2ban Setup**: Currently configured in the nginx-multisite cookbook. Use Ansible's fail2ban modules or templates.
- **SSH Hardening**: Disables root login and password authentication. Use Ansible's `lineinfile` or dedicated SSH hardening role.
- **SSL Certificate Management**: Self-signed certificates are generated for development. Consider using Ansible's `openssl_*` modules or certbot role for production.
- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook (redis_secure_password_123)
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook (user: fastapi, password: fastapi_password)
  - No Chef Vault or encrypted data bags are used, but these credentials should be moved to Ansible Vault

### Technical Challenges

- **Multi-site Configuration**: The nginx-multisite cookbook dynamically creates site configurations based on attributes. This pattern needs to be replicated in Ansible using loops and templates.
- **Service Interdependencies**: The FastAPI application depends on PostgreSQL, and the web server depends on the application. Proper ordering and handlers will be needed in Ansible.
- **Custom SSL Certificate Generation**: The current setup generates self-signed certificates. This logic needs to be replicated or improved in Ansible.
- **Redis Configuration Hack**: The cache cookbook includes a ruby_block to modify Redis configuration files after they're created. This will need special handling in Ansible.

### Migration Order

1. **cache** (Priority 1): Relatively simple cookbook with external dependencies. Start with this to establish patterns for handling external dependencies.
2. **nginx-multisite** (Priority 2): Core infrastructure component with security configurations. Migrate after cache to ensure proper service availability.
3. **fastapi-tutorial** (Priority 3): Application deployment that depends on other services. Migrate last as it depends on both web server and database configurations.

### Assumptions

1. The current Chef setup is primarily for development/testing as evidenced by:
   - Self-signed SSL certificates
   - Hardcoded database credentials
   - Vagrant development environment
   
2. The migration will maintain the same target OS support (Fedora, Ubuntu, CentOS)

3. Security configurations will be preserved or enhanced during migration

4. The FastAPI application source will continue to be pulled from the same Git repository

5. The current multi-site configuration pattern will be maintained in Ansible

6. No specific CI/CD integration is present in the current setup, so none is required in the Ansible migration

7. The Redis configuration "hack" suggests there might be compatibility issues with the Redis version that need to be addressed in Ansible as well

8. No monitoring or logging solutions are configured beyond basic service management