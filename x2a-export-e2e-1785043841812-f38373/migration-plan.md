# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site web application environment with FastAPI backend, Nginx web server, and caching services. The migration to Ansible will involve converting three Chef cookbooks with moderate complexity. The estimated timeline for migration is 2-3 weeks with a single engineer, or 1-2 weeks with a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled subdomains, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site virtual hosts, SSL certificate generation, fail2ban integration, UFW firewall configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

- **cache**:
    - Description: Configures caching services (Memcached and Redis) with security settings
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, log directory management

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies for Chef Berkshelf. Will be replaced with Ansible Galaxy requirements.yml.
- `solo.json`: Contains Chef node attributes and run list. Will be replaced with Ansible inventory variables.
- `solo.rb`: Chef Solo configuration. Will be replaced with Ansible configuration.
- `Vagrantfile`: Defines the development VM. Can be adapted for Ansible with minimal changes.
- `vagrant-provision.sh`: Installs Chef and runs cookbooks. Will be replaced with Ansible provisioning script.

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks

### Security Considerations

- **SSL Certificate Management**: Self-signed certificates are generated for development. Migration should maintain this capability while allowing for production certificates.
  - Migration approach: Use Ansible's openssl_* modules for certificate generation
  
- **Firewall Configuration**: UFW is configured with specific rules for web and SSH access.
  - Migration approach: Use Ansible's ufw module to maintain identical firewall rules

- **SSH Hardening**: SSH configuration disables root login and password authentication.
  - Migration approach: Use Ansible's lineinfile or template module to configure SSH

- **Fail2ban Integration**: Fail2ban is configured for intrusion prevention.
  - Migration approach: Use Ansible's template module to configure fail2ban

- **Vault/secrets management**:
  - Redis password in cache cookbook: "redis_secure_password_123"
  - PostgreSQL credentials in fastapi-tutorial cookbook: User "fastapi" with password "fastapi_password"
  - Total credentials detected: 2 hardcoded passwords

### Technical Challenges

- **Multi-site Configuration**: The nginx-multisite cookbook dynamically creates site configurations based on attributes. 
  - Mitigation: Use Ansible loops with templates to achieve the same dynamic configuration

- **Service Orchestration**: The current setup has interdependent services (Nginx, PostgreSQL, FastAPI application).
  - Mitigation: Use Ansible handlers and proper task ordering to maintain service dependencies

- **SSL Certificate Generation**: Self-signed certificates are generated for each site.
  - Mitigation: Use Ansible's openssl_* modules to generate certificates with similar parameters

### Migration Order

1. **cache** cookbook (low complexity, standalone functionality)
   - Implement Memcached configuration
   - Implement Redis with authentication

2. **fastapi-tutorial** cookbook (moderate complexity)
   - Implement Python environment setup
   - Configure PostgreSQL database
   - Set up application deployment
   - Create systemd service

3. **nginx-multisite** cookbook (highest complexity, depends on other services)
   - Implement base Nginx configuration
   - Configure security features (fail2ban, firewall)
   - Set up SSL certificate generation
   - Create site configurations

### Assumptions

1. The target environment will continue to be Vagrant-based for development/testing
2. Self-signed certificates are acceptable for the migrated solution (production would require proper certificates)
3. The same operating systems (Fedora, Ubuntu, CentOS) will be supported
4. No changes to the application architecture are required during migration
5. Passwords and sensitive data will be migrated as-is initially, with a recommendation to implement Ansible Vault in a future phase
6. The FastAPI application repository URL will remain accessible
7. The current security configurations (firewall rules, SSH hardening) should be maintained in the Ansible version