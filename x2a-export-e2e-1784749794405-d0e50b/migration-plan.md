# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with FastAPI application and caching services (Redis and Memcached). The migration scope includes 3 Chef cookbooks with moderate complexity. Based on the analysis, we estimate a 2-3 week timeline for complete migration, with the most complex components being the Nginx multi-site configuration and the FastAPI application deployment.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled subdomains, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site virtual hosts, SSL configuration, security hardening

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment, Git repository deployment, PostgreSQL database setup, systemd service configuration

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

### Infrastructure Files

- `Berksfile`: Manages cookbook dependencies, including external cookbooks from Chef Supermarket (nginx, memcached, redisio). Will need to be replaced with Ansible Galaxy requirements.
- `solo.json`: Contains the Chef run list and configuration data for Nginx sites and security settings. Will be migrated to Ansible group_vars or host_vars.
- `Vagrantfile`: Defines the development environment using Fedora 42. Can be reused with minimal changes for Ansible testing.
- `vagrant-provision.sh`: Installs Chef and runs the cookbooks. Will need to be replaced with an Ansible-based provisioning script.

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (from Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (from cookbook metadata)
- **Virtual Machine Technology**: Libvirt (from Vagrantfile)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` role or the official `ansible.posix.nginx` collection
- **memcached (~> 6.0)**: Replace with Ansible's `geerlingguy.memcached` role or custom tasks
- **redisio (~> 7.2.4)**: Replace with Ansible's `geerlingguy.redis` role or custom tasks
- **PostgreSQL**: Replace with Ansible's `geerlingguy.postgresql` role or the official `community.postgresql` collection

### Security Considerations

- **SSL Configuration**: The Nginx cookbook manages SSL certificates in `/etc/ssl/certs` and `/etc/ssl/private`. Migration should preserve these paths or update references.
- **Redis Authentication**: Redis is configured with password authentication (`requirepass: 'redis_secure_password_123'`). This password should be migrated to Ansible Vault.
- **PostgreSQL Credentials**: The FastAPI application uses PostgreSQL with hardcoded credentials (`fastapi:fastapi_password`). These should be migrated to Ansible Vault.
- **Security Hardening**: The Nginx configuration includes security hardening via `security.conf.erb`. This should be preserved in the Ansible templates.
- **Fail2ban and UFW**: Security settings in `solo.json` indicate Fail2ban and UFW are enabled. These configurations should be migrated to Ansible tasks.
- **SSH Hardening**: SSH configuration disables root login and password authentication. These settings should be preserved in the Ansible playbooks.
- **Vault/secrets management**: 
  - 2 hardcoded credentials detected in `fastapi-tutorial` cookbook (PostgreSQL username/password)
  - 1 hardcoded credential in `cache` cookbook (Redis password)
  - No Chef Vault or encrypted data bags detected

### Technical Challenges

- **Multi-site Nginx Configuration**: The Nginx cookbook manages multiple virtual hosts with SSL. This will require careful template migration to ensure all sites continue to function.
- **FastAPI Application Deployment**: The FastAPI application deployment includes Git cloning, virtual environment setup, and systemd service configuration. This will require multiple Ansible tasks to replicate.
- **Redis Configuration Hack**: The cache cookbook includes a Ruby block to modify Redis configuration files after deployment. This will need to be reimplemented as an Ansible template or lineinfile task.
- **Service Dependencies**: The FastAPI service depends on PostgreSQL. These dependencies need to be maintained in the Ansible playbooks.

### Migration Order

1. **cache cookbook** (low risk, standalone): Migrate the Redis and Memcached configurations first as they have minimal dependencies.
2. **nginx-multisite cookbook** (moderate complexity): Migrate the Nginx configuration next, focusing on the base configuration before adding virtual hosts.
3. **fastapi-tutorial cookbook** (high complexity): Migrate the FastAPI application deployment last, as it depends on both the database and potentially the Nginx configuration.

### Assumptions

1. The current deployment is targeting a single server environment, as indicated by the Vagrantfile.
2. SSL certificates are self-signed or generated during deployment (no external certificate management is visible).
3. The FastAPI application repository at `https://github.com/dibanez/fastapi_tutorial.git` will remain available.
4. The current Chef setup does not appear to use environment-specific configurations, suggesting a single environment deployment.
5. No CI/CD integration is visible in the current setup, so the Ansible migration will not need to account for existing pipelines.
6. The Nginx sites configuration in `solo.json` suggests three subdomains (`test`, `ci`, and `status`) that will need to be preserved in the Ansible configuration.
7. No monitoring or logging solutions are explicitly configured beyond standard service logs.