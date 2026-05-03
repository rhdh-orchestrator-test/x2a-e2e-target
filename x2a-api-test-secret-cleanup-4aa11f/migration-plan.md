# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The codebase is well-structured with clear separation of concerns
- External dependencies on community cookbooks will need Ansible equivalents
- Security configurations are present and will need careful migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, UFW firewall), custom Nginx configuration

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, dependency on community cookbooks

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Manages cookbook dependencies including external cookbooks from Chef Supermarket (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Defines the Chef run list and configuration attributes for Nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings
- `Vagrantfile`: Defines a Fedora 42 VM with port forwarding for development/testing
- `vagrant-provision.sh`: Bash script to install Chef and run the cookbooks in the Vagrant environment

### Target Details

- **Operating System**: Fedora (based on Vagrantfile specifying "generic/fedora42"), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider (based on Vagrantfile configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or local development environments

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` role or use the `ansible.builtin.package` module with templates
- **memcached (~> 6.0)**: Replace with Ansible's `memcached` role or use the `ansible.builtin.package` module with templates
- **redisio (~> 7.2.4)**: Replace with Ansible's `redis` role or use the `ansible.builtin.package` module with templates
- **Git repository**: Use Ansible's `ansible.builtin.git` module to clone the FastAPI repository
- **Python environment**: Use Ansible's `ansible.builtin.pip` module for Python dependencies

### Security Considerations

- **SSL Certificates**: The current implementation generates self-signed certificates. Migration should:
  - Use Ansible's `openssl_*` modules for certificate generation
  - Consider integration with Let's Encrypt via `community.crypto.acme_certificate`
  - Maintain proper permissions on private keys (640 permissions, ssl-cert group)

- **Firewall Configuration**: The current implementation uses UFW. Migration should:
  - Use Ansible's `ansible.posix.firewalld` module for Fedora/CentOS
  - Use Ansible's `community.general.ufw` module for Ubuntu
  - Maintain the same allow/deny rules (SSH, HTTP, HTTPS)

- **Fail2ban**: Migrate fail2ban configuration using Ansible's `community.general.fail2ban` module

- **SSH Hardening**: Maintain SSH security settings:
  - Disable root login
  - Disable password authentication
  - Use Ansible's `ansible.posix.sshd_config` module

- **Vault/secrets management**:
  - Redis password in cache cookbook: Move to Ansible Vault
  - PostgreSQL credentials in fastapi-tutorial cookbook: Move to Ansible Vault
  - Count of credentials detected: 2 (Redis password, PostgreSQL user/password)

### Technical Challenges

- **Multi-platform Support**: The current cookbooks support both Ubuntu and CentOS/RHEL. Ansible playbooks will need conditional logic for different package managers and service names.
  - Mitigation: Use Ansible's OS family variables and conditionals

- **Custom Resource Migration**: The `lineinfile` custom resource will need to be replaced with Ansible's `ansible.builtin.lineinfile` module.
  - Mitigation: Direct replacement is possible as Ansible's module has similar functionality

- **Redis Configuration Hack**: The cache cookbook contains a hack to fix Redis configuration. This will need special attention.
  - Mitigation: Use Ansible templates with proper conditionals instead of post-configuration modifications

- **Nginx Site Configuration**: The dynamic generation of Nginx site configurations will need to be replicated.
  - Mitigation: Use Ansible templates with loops over site variables

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component
   - Other services depend on it
   - Contains security configurations that should be established first

2. **cache** (Priority 2)
   - Standalone service with external dependencies
   - Moderate complexity due to Redis configuration requirements

3. **fastapi-tutorial** (Priority 3)
   - Application deployment that depends on properly configured infrastructure
   - Contains database setup that should come after core infrastructure

### Assumptions

1. The target environment will continue to be Fedora/CentOS/Ubuntu based on the current cookbook support.
2. Self-signed certificates are acceptable for the migrated solution, but the plan should include options for proper certificate management.
3. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
4. The current security settings (firewall rules, SSH hardening) are appropriate for the target environment.
5. The Vagrant development environment will be maintained, but migrated to use Ansible provisioning instead of Chef.
6. The current Redis password and PostgreSQL credentials are development values that can be replaced during migration.
7. No specific monitoring or logging solutions are currently implemented beyond standard service logs.