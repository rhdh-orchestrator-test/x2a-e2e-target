# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks, handling external dependencies, and ensuring proper security configurations are maintained.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 3-4 weeks
- Testing and Validation: 2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 7-8 weeks

**Complexity Assessment:** Medium to High
- Multiple interconnected services
- Security hardening requirements
- SSL certificate management
- Database integration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and custom configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw), sysctl optimizations

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, log directory management

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file listing cookbook dependencies (nginx, ssl_certificate, memcached, redisio)
- `Policyfile.rb`: Chef policy file defining the run list and cookbook versions
- `solo.json`: Configuration data for Chef Solo with site configurations and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Defines the development VM (Fedora 42) with port forwarding and resource allocation
- `vagrant-provision.sh`: Provisioning script for Vagrant that installs Chef and runs the cookbooks

### Target Details

- **Operating System**: Fedora (based on Vagrantfile using "generic/fedora42"), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role (e.g., geerlingguy.nginx or custom role)
- **ssl_certificate (~> 2.1)**: Replace with Ansible modules for certificate management (openssl_* modules)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role (e.g., geerlingguy.redis or DavidWittman.redis)

### Security Considerations

- **SSL Certificate Management**: The Chef cookbook generates self-signed certificates. Ansible migration should use the `openssl_certificate` module to maintain this functionality or integrate with Let's Encrypt using `community.crypto.acme_certificate`.
- **Firewall Configuration**: The Chef cookbook configures UFW. Ansible migration should use the `ansible.posix.ufw` module to maintain firewall rules.
- **Fail2ban Configuration**: The Chef cookbook configures fail2ban. Ansible migration should use appropriate modules to configure fail2ban.
- **SSH Hardening**: The Chef cookbook disables root login and password authentication. Ansible migration should maintain these security practices using the `ansible.posix.ssh_config` module.
- **Redis Authentication**: The Chef cookbook sets a Redis password. Ansible migration should maintain this security practice.
- **PostgreSQL Security**: The Chef cookbook creates a PostgreSQL user with a password. Ansible migration should use the `community.postgresql` collection to maintain secure database configuration.

### Technical Challenges

- **Multi-site Nginx Configuration**: The Chef cookbook dynamically creates Nginx site configurations based on node attributes. Ansible migration will need to use templates and loops to achieve similar functionality.
- **SSL Certificate Generation**: The Chef cookbook generates self-signed certificates. Ansible migration will need to replicate this functionality or improve it with Let's Encrypt integration.
- **System Tuning**: The Chef cookbook configures sysctl parameters. Ansible migration will need to use the `ansible.posix.sysctl` module to maintain these optimizations.
- **Service Orchestration**: The Chef cookbook manages multiple interdependent services. Ansible migration will need to carefully handle service dependencies and notifications.
- **Python Environment Management**: The Chef cookbook creates and manages a Python virtual environment. Ansible migration will need to use the `pip` module with the `virtualenv` parameter to maintain this functionality.

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Create base Nginx role
   - Implement SSL certificate generation
   - Configure virtual hosts
   - Implement security hardening

2. **cache** (moderate complexity, depends on network infrastructure)
   - Create Memcached role
   - Create Redis role with authentication
   - Configure log directories and service management

3. **fastapi-tutorial** (high complexity, depends on other components)
   - Create PostgreSQL role
   - Create Python application deployment role
   - Configure systemd service
   - Set up environment variables

### Assumptions

1. The target environment will continue to be Fedora-based, with potential for Ubuntu and CentOS as mentioned in the cookbook metadata.
2. Self-signed certificates are acceptable for development, but production may require proper CA-signed certificates.
3. The security hardening measures in the current Chef cookbooks are appropriate and should be maintained in the Ansible roles.
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
5. The Redis password "redis_secure_password_123" and PostgreSQL password "fastapi_password" are development passwords that should be replaced with secure, environment-specific passwords in production.
6. The current Vagrant-based development workflow should be maintained, but with Ansible provisioning instead of Chef.
7. The current port mappings and network configurations are appropriate and should be maintained.
8. No specific monitoring or logging solutions are currently implemented beyond basic service logs.