# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated timeline for this migration is 3-4 weeks, with moderate complexity due to the security configurations and multiple service integrations.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and self-signed certificate generation
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL/TLS setup, security hardening (fail2ban, UFW firewall), sysctl security settings

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database provisioning, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks. Lists both local and external cookbook dependencies with version constraints.
- `solo.json`: Chef configuration file containing the run list and node attributes. Defines Nginx site configurations and security settings.
- `solo.rb`: Chef configuration file specifying cookbook paths and logging settings.
- `Vagrantfile`: Defines a Fedora 42 VM with networking and resource configurations for local development and testing.
- `vagrant-provision.sh`: Shell script that installs Chef and its dependencies, and runs the Chef provisioning process.

### Target Details

- **Operating System**: Fedora (based on Vagrantfile specifying "generic/fedora42"), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or nginx_core module
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks

### Security Considerations

- **Firewall Configuration**: UFW firewall rules need to be migrated to equivalent Ansible ufw module or firewalld for Fedora
- **Fail2ban Setup**: Configuration needs to be migrated to Ansible tasks using templates
- **SSH Hardening**: SSH configuration (disabling root login, password authentication) needs to be migrated
- **SSL/TLS Management**: Self-signed certificate generation needs to be handled with Ansible crypto modules
- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook (`fastapi:fastapi_password`)
  - These should be migrated to Ansible Vault or another secrets management solution

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of multiple virtual hosts with SSL needs careful planning in Ansible
- **Service Orchestration**: The interdependencies between services (PostgreSQL before FastAPI, Nginx configuration) need to be maintained
- **Redis Configuration**: The Redis configuration includes some custom modifications and workarounds that need special attention
- **Python Environment Management**: The Python virtual environment setup and dependency installation needs to be properly handled in Ansible

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Start with basic Nginx installation and configuration
   - Add security hardening (fail2ban, firewall)
   - Implement SSL certificate generation
   - Configure virtual hosts

2. **cache** (low complexity, independent service)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Set up PostgreSQL database and user
   - Deploy FastAPI application from Git
   - Configure Python environment and dependencies
   - Set up systemd service

### Assumptions

1. The target environment will continue to be Fedora-based, though the cookbooks support Ubuntu and CentOS as well
2. The self-signed certificates approach will be maintained rather than implementing Let's Encrypt or another certificate authority
3. The current security configurations (fail2ban, UFW, SSH hardening) are appropriate for the target environment
4. The Redis and PostgreSQL passwords in the code are development/testing credentials and will be replaced with proper secrets management in production
5. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
6. The current VM specifications (2GB RAM, 2 CPUs) are sufficient for the application stack
7. No additional monitoring or logging solutions need to be implemented beyond what's in the current Chef configuration