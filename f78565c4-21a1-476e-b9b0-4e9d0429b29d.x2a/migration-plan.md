# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks, handling external dependencies, and ensuring proper security configurations are maintained.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 3-4 weeks
- Testing and Validation: 2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 7-8 weeks

**Complexity Assessment:** Medium to High
- Multiple interconnected services
- Security configurations that need careful migration
- SSL certificate management
- Database integration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site-specific configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, UFW firewall)

- **cache**:
    - Description: Configures Redis and Memcached caching services with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies (nginx, ssl_certificate, memcached, redisio)
- `Policyfile.rb`: Defines the run list and cookbook dependencies
- `solo.json`: Contains node configuration data including Nginx site configurations and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Defines the development VM (Fedora 42) with port forwarding and networking
- `vagrant-provision.sh`: Bash script to provision the VM with Chef

### Target Details

- **Operating System**: Fedora (based on Vagrantfile using "generic/fedora42"), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or collection (e.g., `ansible.posix.nginx`)
- **ssl_certificate (~> 2.1)**: Replace with Ansible's `community.crypto` collection for certificate management
- **memcached (~> 6.0)**: Replace with Ansible memcached role or direct package installation
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role or direct package installation and configuration

### Security Considerations

- **SSL Certificate Management**: Migration must maintain proper certificate generation and permissions
  - Self-signed certificates are currently generated with OpenSSL
  - Proper file permissions (640) and ownership (root:ssl-cert) must be preserved

- **Firewall Configuration**: UFW firewall rules must be migrated
  - Default deny policy
  - Allow SSH, HTTP, HTTPS

- **fail2ban Integration**: Configuration must be preserved
  - Current setup uses a custom jail.local template

- **SSH Hardening**: Security settings must be maintained
  - Root login disabled
  - Password authentication disabled

- **System Hardening**: sysctl security settings must be migrated
  - Custom sysctl-security.conf template

- **Redis Authentication**: Password authentication must be preserved
  - Current password: "redis_secure_password_123" (should be changed and stored securely)

- **PostgreSQL Security**: Database credentials must be migrated securely
  - Current credentials: User "fastapi" with password "fastapi_password" (should be changed and stored securely)

### Technical Challenges

- **Multi-site Nginx Configuration**: The current setup dynamically generates site configurations based on node attributes. Ansible will need to replicate this dynamic configuration approach.
  - Solution: Use Ansible templates with loops over site definitions in variables

- **SSL Certificate Generation**: Self-signed certificates are generated for each site. This process needs to be replicated in Ansible.
  - Solution: Use the `community.crypto.openssl_*` modules to generate certificates

- **Service Orchestration**: The current setup has interdependent services (Nginx, Redis, Memcached, PostgreSQL, FastAPI application).
  - Solution: Use Ansible handlers and dependencies to ensure proper service ordering

- **Python Application Deployment**: The FastAPI application deployment includes git cloning, virtual environment setup, and systemd service configuration.
  - Solution: Use Ansible's git, pip, and systemd modules to replicate this functionality

### Migration Order

1. **cache** (Priority 1 - Low complexity)
   - Simple Redis and Memcached configuration
   - Good starting point with minimal dependencies

2. **nginx-multisite** (Priority 2 - Medium complexity)
   - Core web server configuration
   - Security hardening components
   - SSL certificate management

3. **fastapi-tutorial** (Priority 3 - Higher complexity)
   - Application deployment
   - Database integration
   - Depends on web server for serving

### Assumptions

1. The target environment will continue to use Fedora or a compatible Linux distribution.
2. Self-signed certificates are acceptable for the migrated environment (not using Let's Encrypt or other CA).
3. The current security configurations are appropriate and should be maintained in the Ansible implementation.
4. The FastAPI application source will continue to be available at the specified Git repository.
5. The current directory structure in the target environment (/opt/fastapi-tutorial, /etc/ssl/*, etc.) should be preserved.
6. The current passwords in the code are for development only and will be replaced with secure values in the production Ansible implementation.
7. The Vagrant development environment will be replaced with an Ansible-compatible alternative.