# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains three Chef cookbooks that manage a multi-site Nginx web server, caching services (Memcached and Redis), and a FastAPI Python application with PostgreSQL. The migration to Ansible will require converting Chef recipes, templates, and attributes to Ansible roles, tasks, templates, and variables. The estimated timeline for migration is 3-4 weeks, with moderate complexity due to the interdependencies between services and security configurations.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and self-signed certificate generation
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL/TLS setup, security hardening (fail2ban, UFW firewall)

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository deployment, Python virtual environment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks. Lists both local and external cookbook dependencies with version constraints.
- `Vagrantfile`: Defines a Fedora 42 VM for local development and testing with port forwarding and resource allocation.
- `solo.json`: Chef Solo configuration file containing the run list and node attributes for Nginx sites and security settings.
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and logging settings.
- `vagrant-provision.sh`: Bash script to provision the Vagrant VM with Chef Solo, installing dependencies and running the cookbooks.

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration) with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create custom Ansible tasks for Nginx installation and configuration
- **memcached (~> 6.0)**: Replace with Ansible Galaxy role `geerlingguy.memcached` or custom Ansible tasks
- **redisio (~> 7.2.4)**: Replace with Ansible Galaxy role `geerlingguy.redis` or custom Ansible tasks for Redis installation and configuration
- **PostgreSQL**: Use Ansible Galaxy role `geerlingguy.postgresql` or custom Ansible tasks for PostgreSQL installation and database setup

### Security Considerations

- **SSL/TLS Certificates**: Migration must handle self-signed certificate generation for development environments
  - Approach: Use Ansible's `openssl_*` modules to generate certificates and keys
  
- **Firewall Configuration**: UFW firewall rules need to be migrated
  - Approach: Use Ansible's `ufw` module to configure firewall rules

- **fail2ban Configuration**: Intrusion prevention settings need to be migrated
  - Approach: Use Ansible to install and configure fail2ban with appropriate jail settings

- **SSH Hardening**: SSH security settings (disable root login, password authentication)
  - Approach: Use Ansible's `lineinfile` module or the `ansible.posix.sshd` module to configure SSH settings

- **Vault/secrets management**:
  - Redis password in cache cookbook: 1 hardcoded password in the recipe
  - PostgreSQL credentials in fastapi-tutorial cookbook: 2 hardcoded passwords in the recipe
  - Environment variables in .env file: Contains database connection string with credentials
  - Approach: Use Ansible Vault to encrypt sensitive values and reference them in playbooks

### Technical Challenges

- **Multi-site Nginx Configuration**: The Chef cookbook dynamically generates Nginx site configurations based on node attributes
  - Mitigation: Create Ansible templates for Nginx site configurations and use Ansible loops to iterate through site definitions

- **Redis Configuration Hacks**: The Chef cookbook includes a ruby_block to modify Redis configuration files after installation
  - Mitigation: Create custom Redis configuration templates in Ansible to avoid post-installation modifications

- **Service Interdependencies**: The FastAPI application depends on PostgreSQL, and Nginx depends on the FastAPI service
  - Mitigation: Use Ansible handlers and the `notify` mechanism to manage service restarts and dependencies

- **SSL Certificate Management**: Self-signed certificates are generated for each Nginx site
  - Mitigation: Create an Ansible role specifically for SSL certificate management with proper conditionals

### Migration Order

1. **cache** (Priority 1 - low complexity)
   - Simple installation and configuration of Memcached and Redis
   - Few dependencies on other modules

2. **fastapi-tutorial** (Priority 2 - moderate complexity)
   - Python application deployment with PostgreSQL database
   - Includes service configuration and environment setup

3. **nginx-multisite** (Priority 3 - high complexity)
   - Complex configuration with multiple sites, SSL, and security features
   - Depends on the FastAPI application being available

### Assumptions

1. The target environment will continue to be Fedora 42 or a compatible Linux distribution.
2. Self-signed certificates are acceptable for the migrated environment (production would likely require proper certificates).
3. The same directory structure (/opt/fastapi-tutorial, /etc/nginx, etc.) will be maintained in the Ansible deployment.
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
5. The security requirements (fail2ban, UFW, SSH hardening) will remain the same in the migrated environment.
6. Redis and Memcached configurations will maintain the same port numbers and basic settings.
7. The Nginx sites (test.cluster.local, ci.cluster.local, status.cluster.local) will remain the same in the migrated environment.
8. The migration will not include changes to the application code or database schema.