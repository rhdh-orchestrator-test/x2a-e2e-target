# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application with PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium to High
- Multiple interconnected services
- SSL certificate management
- Security configurations
- Database integration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, fail2ban integration, UFW firewall rules

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

- `Berksfile`: Defines cookbook dependencies (nginx, ssl_certificate, memcached, redisio) - will be replaced by Ansible Galaxy requirements.yml
- `Policyfile.rb`: Defines the run list and cookbook versions - will be replaced by Ansible playbook structure
- `solo.json`: Contains node attributes and run list - will be converted to Ansible variables
- `solo.rb`: Chef Solo configuration - not needed in Ansible
- `Vagrantfile`: VM configuration for development/testing - can be adapted for Ansible testing
- `vagrant-provision.sh`: Provisioning script for Vagrant - will be replaced by Ansible provisioning

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile configuration)
- **Cloud Platform**: Not specified, appears to be designed for on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Nginx role
- **ssl_certificate (~> 2.1)**: Replace with Ansible's `openssl_*` modules for certificate management
- **memcached (~> 6.0)**: Replace with Ansible Galaxy role `geerlingguy.memcached`
- **redisio (~> 7.2.4)**: Replace with Ansible Galaxy role `geerlingguy.redis` or DavidWittman.redis

### Security Considerations

- **SSL Certificate Management**: The current implementation generates self-signed certificates. Ansible's `openssl_*` modules can handle this, but consider integrating with Let's Encrypt for production.
- **Firewall Configuration**: UFW rules need to be migrated to Ansible's `ufw` module or `firewalld` module for RHEL-based systems.
- **fail2ban Integration**: Migrate fail2ban configuration to Ansible using templates and service management.
- **SSH Hardening**: Current configuration disables root login and password authentication. Migrate to Ansible's `lineinfile` module or a dedicated SSH hardening role.
- **Redis Password**: The Redis password is hardcoded in the recipe. Move to Ansible Vault for secure storage.

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of site configurations based on node attributes will need to be replicated using Ansible's templating system.
- **SSL Certificate Generation**: Self-signed certificate generation logic needs to be migrated to Ansible tasks.
- **PostgreSQL User and Database Creation**: The current implementation uses direct commands. Consider using Ansible's PostgreSQL modules for better idempotence.
- **Service Dependencies**: Ensuring proper ordering of service installation and configuration, especially for the FastAPI application which depends on PostgreSQL.

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Start with basic Nginx installation and configuration
   - Add virtual host configuration
   - Implement SSL certificate generation
   - Add security configurations (fail2ban, UFW, headers)

2. **cache** (Priority 2)
   - Implement Memcached configuration
   - Implement Redis with authentication
   - Ensure proper integration with Nginx

3. **fastapi-tutorial** (Priority 3)
   - Set up PostgreSQL database
   - Deploy FastAPI application
   - Configure systemd service
   - Integrate with Nginx for proxying

### Assumptions

1. The target environment will continue to be Fedora/RHEL-based systems, with potential support for Ubuntu/Debian.
2. Self-signed certificates are acceptable for development, but production deployment may require proper CA-signed certificates.
3. The current security configurations (fail2ban, UFW, SSH hardening) are appropriate for the target environment.
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
5. The current Redis password and PostgreSQL credentials are development values and will be replaced with secure values in production.
6. The Vagrant setup is primarily for development and testing, not production deployment.
7. No custom Nginx modules or configurations beyond what's visible in the templates are required.
8. The current directory structure in `/opt/server/` for website content and `/opt/fastapi-tutorial/` for the application will be maintained.