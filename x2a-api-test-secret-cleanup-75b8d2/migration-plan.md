# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure for deploying a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI Python application with PostgreSQL database. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:**
- Medium complexity due to multiple services and security configurations
- Security considerations for credentials and SSL certificates
- Integration between multiple components (web server, caching, application)

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site-specific configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw firewall)

- **cache**:
    - Description: Configures Memcached and Redis caching services with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies including nginx (~> 12.0), memcached (~> 6.0), and redisio (~> 7.2.4)
- `solo.json`: Contains configuration data for Nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file
- `vagrant-provision.sh`: Bash script for provisioning Chef in a Vagrant VM
- `Vagrantfile`: Defines VM configuration using Fedora 42 with port forwarding for HTTP/HTTPS

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (as specified in the Vagrantfile)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for local development/testing

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or nginx_core module
- **memcached (~> 6.0)**: Replace with Ansible memcached role
- **redisio (~> 7.2.4)**: Replace with Ansible redis role
- **PostgreSQL**: Replace with Ansible postgresql role or postgresql_* modules

### Security Considerations

- **SSL Certificates**: 
  - Self-signed certificates are generated for each site
  - Migration should use Ansible's openssl_* modules or community.crypto collection
  - Consider integrating with Let's Encrypt for production environments

- **Firewall Configuration**: 
  - UFW firewall rules should be migrated to Ansible's ufw module
  - Default deny policy with specific allows for SSH, HTTP, HTTPS

- **Fail2ban**: 
  - Configuration should be migrated to Ansible's template module
  - Consider using community.general.fail2ban module for management

- **SSH Hardening**:
  - Disable root login and password authentication
  - Use Ansible's lineinfile or template module for sshd_config

- **Vault/secrets management**:
  - Redis password: "redis_secure_password_123" in cache/recipes/default.rb
  - PostgreSQL credentials: username "fastapi", password "fastapi_password" in fastapi-tutorial/recipes/default.rb
  - These should be moved to Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Challenge: Dynamically creating multiple virtual hosts with SSL
  - Solution: Use Ansible loops with templates for site configuration

- **SSL Certificate Management**: 
  - Challenge: Generating and managing SSL certificates for multiple domains
  - Solution: Use Ansible's crypto modules or certbot role for Let's Encrypt integration

- **Service Dependencies**: 
  - Challenge: Ensuring proper service startup order (PostgreSQL before FastAPI)
  - Solution: Use Ansible handlers and meta dependencies between roles

- **Idempotent Execution**: 
  - Challenge: Ensuring commands like database creation run only when needed
  - Solution: Use Ansible's changed_when, failed_when, and register to control execution flow

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Create base Nginx configuration and security hardening first

2. **cache** (Priority 2)
   - Relatively simple configuration for Memcached and Redis
   - Independent of other services

3. **fastapi-tutorial** (Priority 3)
   - Most complex with database, application deployment, and service configuration
   - Depends on proper web server configuration for access

### Assumptions

1. The target environment will continue to be Fedora-based systems
2. Self-signed certificates are acceptable for development, but production may require proper CA-signed certificates
3. The current security configurations (fail2ban, ufw, SSH hardening) are appropriate for the target environment
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current port mappings (80/443 internally, 8080/8443 forwarded) will be maintained
6. The current VM resource allocation (2GB RAM, 2 CPUs) is sufficient for the application stack
7. No additional monitoring or logging solutions are required beyond what's currently implemented
8. The migration will maintain the same directory structure for web content (/var/www/*)
9. PostgreSQL will continue to be used as the database backend for the FastAPI application
10. The current Redis and Memcached configurations are sufficient for the application's caching needs