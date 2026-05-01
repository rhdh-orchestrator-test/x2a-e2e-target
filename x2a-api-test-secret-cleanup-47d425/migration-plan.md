# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI application with PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies, security configurations, and service deployments. Based on the complexity and scope, this migration is estimated to take 2-3 weeks with a team of 2 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and fail2ban integration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL/TLS setup with self-signed certificates, security headers, fail2ban integration, UFW firewall configuration

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, log directory management

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository deployment, Python virtual environment setup, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file listing cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `Vagrantfile`: Development environment configuration using Fedora 42, with port forwarding and resource allocation
- `solo.json`: Chef Solo configuration with run list and node attributes for nginx sites and security settings
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings
- `vagrant-provision.sh`: Provisioning script for Vagrant that installs Chef and runs the cookbooks

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or direct package installation and configuration
- **PostgreSQL**: Replace with Ansible postgresql_* modules or community.postgresql collection

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the SSL configuration with proper certificate generation and secure settings
  - Migration approach: Use ansible.builtin.openssl_* modules for certificate generation and template the nginx SSL configuration
  
- **Fail2ban Integration**: Security hardening with fail2ban must be maintained
  - Migration approach: Use ansible.posix.fail2ban module or direct configuration file templating

- **Firewall Rules**: UFW firewall configuration must be migrated
  - Migration approach: Use ansible.posix.ufw module to configure firewall rules

- **System Hardening**: Sysctl security settings must be preserved
  - Migration approach: Use ansible.posix.sysctl module to apply system security settings

- **Vault/secrets management**:
  - Redis password in cache cookbook (hardcoded as 'redis_secure_password_123')
  - PostgreSQL database credentials in fastapi-tutorial cookbook (hardcoded as 'fastapi_password')
  - Total credentials detected: 2 hardcoded passwords that should be moved to Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: The current setup uses Chef templates to generate multiple virtual host configurations
  - Mitigation: Create Ansible templates with similar logic and use with_items to iterate over site configurations

- **Redis Configuration Hack**: The current setup includes a Ruby block to modify Redis configuration files after installation
  - Mitigation: Create a custom Redis configuration template in Ansible that doesn't require post-installation modifications

- **Service Orchestration**: The current setup manages service dependencies and notifications
  - Mitigation: Use Ansible handlers and meta dependencies to ensure proper service restart ordering

- **SSL Certificate Generation**: Self-signed certificates are generated for each virtual host
  - Mitigation: Use ansible.builtin.openssl_* modules with similar parameters to generate certificates

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Start with basic Nginx installation and configuration
   - Add security configurations (fail2ban, UFW, sysctl)
   - Implement multi-site virtual host configuration with SSL

2. **cache** (moderate complexity, depends on external modules)
   - Implement Memcached configuration
   - Implement Redis with authentication
   - Ensure proper service management

3. **fastapi-tutorial** (high complexity, application deployment)
   - Set up PostgreSQL database and user
   - Configure Python environment and dependencies
   - Deploy application from Git
   - Create systemd service configuration

### Assumptions

1. The target environment will continue to be Fedora 42 or a compatible Linux distribution
2. The same directory structure will be maintained for document roots and application files
3. Self-signed certificates are acceptable for the migrated environment (not production)
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The hardcoded passwords in the current configuration will be replaced with Ansible Vault variables
6. The current security settings (fail2ban, UFW, sysctl) are appropriate for the target environment
7. The Nginx virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local) will remain the same
8. The current service ports (80/443 for Nginx, 6379 for Redis, 8000 for FastAPI) will be maintained