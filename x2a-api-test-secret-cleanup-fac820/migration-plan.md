# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup with three main cookbooks: nginx-multisite, cache, and fastapi-tutorial. The migration to Ansible will involve converting Chef recipes, templates, and attributes to Ansible roles, tasks, templates, and variables. The estimated timeline for this migration is 3-4 weeks, with moderate complexity due to the interdependencies between components and security configurations.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and custom configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw), custom Nginx configurations

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, log directory management

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks. Lists both local and external cookbook dependencies with version constraints.
- `solo.json`: Chef configuration file defining the run list and node attributes. Contains site configurations and security settings.
- `solo.rb`: Chef configuration file specifying cookbook paths and logging settings.
- `Vagrantfile`: Defines a Vagrant VM configuration using Fedora 42 with port forwarding and resource allocation.
- `vagrant-provision.sh`: Shell script that installs Chef and Berkshelf, then runs Chef Solo to provision the VM.

### Target Details

- **Operating System**: Fedora (based on Vagrantfile specifying "generic/fedora42"), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider (based on Vagrantfile configuration)
- **Cloud Platform**: Not specified, appears to be targeting local development/testing environment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` module and community.general collection
- **memcached (~> 6.0)**: Replace with Ansible's `apt`/`yum` modules and template configurations
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role from Galaxy or custom tasks using package, template, and service modules

### Security Considerations

- **SSL Certificate Management**: 
  - Migration approach: Use Ansible's `openssl_*` modules to generate self-signed certificates
  - Consider integration with Let's Encrypt using `community.crypto.acme_certificate`

- **Firewall Configuration (UFW)**:
  - Migration approach: Use Ansible's `community.general.ufw` module to configure firewall rules

- **Fail2ban Configuration**:
  - Migration approach: Use Ansible package and template modules to install and configure fail2ban

- **SSH Hardening**:
  - Migration approach: Use Ansible's `lineinfile` or templates to configure SSH security settings

- **Vault/secrets management**:
  - Redis password in cache cookbook (hardcoded as 'redis_secure_password_123')
  - PostgreSQL database credentials in fastapi-tutorial cookbook (hardcoded as 'fastapi_password')
  - Consider using Ansible Vault to secure these credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of multiple virtual hosts based on node attributes will require careful translation to Ansible variables and templates.
  - Mitigation: Create a structured variable format in Ansible and use with_items/loop to iterate through site configurations.

- **Redis Configuration Hack**: The Chef cookbook uses a ruby_block to modify Redis configuration files after they're created.
  - Mitigation: Create a proper Redis configuration template in Ansible that doesn't require post-processing.

- **Service Orchestration**: The current setup has interdependencies between services (e.g., FastAPI depends on PostgreSQL).
  - Mitigation: Use Ansible handlers and proper task ordering to ensure services start in the correct sequence.

- **SSL Certificate Generation**: The current setup generates self-signed certificates using inline shell commands.
  - Mitigation: Use Ansible's `openssl_*` modules for cleaner, idempotent certificate management.

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for web services)
   - Start with basic Nginx installation and configuration
   - Add SSL certificate generation
   - Implement security hardening (fail2ban, ufw)
   - Configure virtual hosts

2. **cache** (low complexity, independent service)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, depends on database)
   - Set up PostgreSQL database
   - Deploy Python application
   - Configure systemd service

### Assumptions

1. The target environment will continue to be Fedora-based, though the cookbooks support Ubuntu and CentOS as well.
2. Self-signed certificates are acceptable for the migrated solution (production environments would likely use Let's Encrypt or proper certificates).
3. The security configurations (fail2ban, ufw, SSH hardening) are still required in the Ansible version.
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git is still available and the correct source.
5. The current hardcoded credentials will be replaced with more secure solutions using Ansible Vault.
6. The Vagrant development environment will be maintained, but converted to use Ansible provisioning instead of Chef.
7. The current directory structure in the target environment (/opt/server/*, /etc/ssl/*) should be preserved in the migration.
8. The Redis configuration hack is a workaround for compatibility issues that may need to be addressed differently in Ansible.