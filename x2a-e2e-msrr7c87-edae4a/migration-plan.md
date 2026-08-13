# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration scope is moderate, consisting of three primary cookbooks with external dependencies. Based on the complexity and size, we estimate a 2-3 week timeline for complete migration, with the most complex components being the Nginx multi-site SSL configuration and the FastAPI application deployment.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate management, security hardening (fail2ban, ufw)

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

- `Berksfile`: Manages cookbook dependencies, including local and external cookbooks. Migration will require mapping these dependencies to Ansible Galaxy roles or collections.
- `solo.json`: Contains the run list and configuration data for Chef Solo. This will be migrated to Ansible inventory variables and group_vars.
- `solo.rb`: Chef Solo configuration file. Will be replaced by Ansible configuration.
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef. Will need to be updated to use Ansible provisioner.
- `Vagrantfile`: Defines the development VM. Will need modification to use Ansible provisioner instead of Chef.

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (from Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (from cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting on-premises or local development environments

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible `nginx` role from Galaxy or use the `ansible.builtin.package` module with templates
- **memcached (~> 6.0)**: Replace with Ansible `geerlingguy.memcached` role or direct configuration
- **redisio (~> 7.2.4)**: Replace with Ansible `geerlingguy.redis` role or direct configuration

### Security Considerations

- **SSL Certificate Management**: The nginx-multisite cookbook manages SSL certificates. Migration should preserve certificate paths and permissions.
  - Migration approach: Use Ansible's `ansible.builtin.copy` or `ansible.builtin.template` modules for certificate deployment, with appropriate file permissions.

- **Redis Authentication**: Redis is configured with password authentication.
  - Migration approach: Use Ansible Vault to store the Redis password and configure Redis with the `geerlingguy.redis` role or custom tasks.

- **Security Hardening**: The configuration includes fail2ban, ufw firewall, and SSH hardening.
  - Migration approach: Use dedicated Ansible roles like `geerlingguy.security` or create tasks for each security component.

- **Vault/secrets management**: 
  - Redis password hardcoded in the cache cookbook
  - PostgreSQL credentials hardcoded in the FastAPI application cookbook
  - FastAPI environment variables with potential sensitive information
  - Total count: 3 credential sets detected

### Technical Challenges

- **Multi-site Nginx Configuration**: The nginx-multisite cookbook manages multiple virtual hosts with SSL. This requires careful template migration.
  - Mitigation: Create Jinja2 templates that replicate the ERB templates from the Chef cookbook, ensuring all site configurations are preserved.

- **PostgreSQL Database Setup**: The FastAPI application requires specific PostgreSQL configuration.
  - Mitigation: Use the `community.postgresql` collection to manage database users and permissions.

- **FastAPI Application Deployment**: The application deployment includes Git checkout, virtual environment setup, and systemd service configuration.
  - Mitigation: Break this into discrete Ansible tasks for each step, ensuring idempotence.

### Migration Order

1. **cache cookbook** (low risk, standalone): Migrate the Redis and Memcached configuration first as they are relatively isolated services.
2. **nginx-multisite cookbook** (moderate complexity): Migrate the Nginx configuration next, as it's a critical component but doesn't depend on the application.
3. **fastapi-tutorial cookbook** (high complexity): Migrate the application deployment last, as it has the most dependencies and complexity.

### Assumptions

1. The current Chef setup is functional and represents the desired state.
2. The target environment will continue to use Vagrant for development/testing.
3. The SSL certificates are self-signed for development (based on Vagrant setup).
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git is accessible and contains the expected code.
5. The migration will maintain the same directory structure for application deployment (/opt/fastapi-tutorial).
6. The PostgreSQL database configuration (users, passwords, database names) should remain the same.
7. Redis configuration quirks (the "fix_redis_config" hack) need to be maintained in the Ansible version.
8. The Nginx sites configuration in solo.json represents all required virtual hosts.