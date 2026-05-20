# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site web server with caching services and a FastAPI application. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated timeline for migration is 3-4 weeks, with moderate complexity due to the interdependencies between services and security configurations.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and custom site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw, sysctl), custom site templates

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, log directory management

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database provisioning, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external cookbook dependencies with version constraints
- `solo.json`: Chef configuration file defining the run list and node attributes for nginx sites and security settings
- `solo.rb`: Chef configuration file specifying cookbook paths and log settings
- `Vagrantfile`: Defines the development VM configuration using Fedora 42, with port forwarding and network settings
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef and run the cookbooks

### Target Details

Based on the source repository analysis:

- **Operating System**: The configuration supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with the development environment using Fedora 42
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks with custom configuration
- **ssl_certificate**: Replace with Ansible OpenSSL modules for certificate generation

### Security Considerations

- **Firewall Configuration**: The Chef cookbook configures UFW; migration should use Ansible's firewall modules (ufw or firewalld depending on target OS)
- **Fail2ban Setup**: Convert fail2ban configuration to Ansible tasks using templates
- **SSH Hardening**: Preserve SSH security settings (disable root login, password authentication)
- **System Hardening**: Migrate sysctl security settings
- **Vault/secrets management**:
  - Redis password in cache cookbook: Should be moved to Ansible Vault
  - PostgreSQL credentials in fastapi-tutorial cookbook: Should be moved to Ansible Vault
  - SSL private keys: Ensure proper permissions and secure handling

### Technical Challenges

- **Multi-site Nginx Configuration**: The current setup dynamically generates site configurations based on node attributes; Ansible implementation will need to use templates with variable substitution
- **SSL Certificate Generation**: Self-signed certificate generation logic needs to be replicated in Ansible
- **Custom Resource Migration**: The `lineinfile` custom resource will need to be replaced with Ansible's lineinfile module
- **Service Dependencies**: Ensuring proper ordering of service installation and configuration, particularly for the FastAPI application which depends on PostgreSQL

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - First implement basic Nginx installation and configuration
   - Then implement security hardening (fail2ban, ufw, sysctl)
   - Finally implement SSL and site configuration

2. **cache** (low complexity, standalone service)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Implement PostgreSQL installation and configuration
   - Implement Python environment setup and application deployment
   - Configure systemd service

### Assumptions

1. The target environment will continue to be Linux-based (Ubuntu, CentOS, or Fedora)
2. Self-signed certificates are acceptable for development/testing (production would likely use Let's Encrypt or other CA)
3. The current security configurations are appropriate for the target environment
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The Redis configuration hack in the cache cookbook is a workaround for compatibility issues that may not be needed in Ansible
6. The current directory structure in /opt/server/ for website content will be maintained
7. The current PostgreSQL authentication method (password) will be maintained rather than switching to more secure methods
8. The current hardcoded credentials will be migrated to Ansible Vault without changing them