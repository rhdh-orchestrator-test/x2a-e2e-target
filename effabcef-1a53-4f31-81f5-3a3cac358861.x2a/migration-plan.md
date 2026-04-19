# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies, configuration templates, and security settings. The estimated timeline for migration is 2-3 weeks with a team of 2 engineers, considering the moderate complexity of the configurations and security requirements.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and fail2ban/ufw firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, firewall configuration

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment, Git repository deployment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file listing cookbook dependencies (nginx, memcached, redisio)
- `Vagrantfile`: Defines a Fedora 42 VM for local development with port forwarding and networking
- `solo.json`: Chef configuration file with run list and node attributes
- `solo.rb`: Chef configuration file with cookbook paths and log settings
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for local development or on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks

### Security Considerations

- **SSL Certificate Management**: The current implementation generates self-signed certificates. Migration should maintain this capability or integrate with Let's Encrypt.
- **Firewall Configuration**: UFW firewall rules need to be migrated to equivalent Ansible firewall modules.
- **Fail2ban Configuration**: Fail2ban setup needs to be migrated to Ansible tasks.
- **Security Headers**: Nginx security headers configuration needs to be preserved in templates.
- **SSH Hardening**: SSH configuration hardening (disable root login, password authentication) needs to be migrated.
- **Vault/secrets management**: 
  - Redis password in cache cookbook (plaintext in recipe)
  - PostgreSQL credentials in fastapi-tutorial cookbook (plaintext in recipe)
  - Total credentials detected: 2 (Redis password, PostgreSQL user/password)

### Technical Challenges

- **Multi-site Configuration**: The dynamic generation of multiple Nginx site configurations needs to be preserved in Ansible.
- **Service Dependencies**: Ensuring proper ordering of service installation and configuration, particularly for the FastAPI application which depends on PostgreSQL.
- **Template Migration**: Converting ERB templates to Jinja2 format for Ansible, particularly for the Nginx site configuration.
- **Security Hardening**: Ensuring all security measures are properly implemented in Ansible.

### Migration Order

1. **nginx-multisite cookbook** (moderate complexity, foundation for other services)
   - First migrate the basic Nginx installation and configuration
   - Then add SSL certificate generation
   - Finally add security hardening features (fail2ban, ufw)

2. **cache cookbook** (low complexity, independent service)
   - Migrate Memcached configuration
   - Migrate Redis configuration with authentication

3. **fastapi-tutorial cookbook** (high complexity, depends on PostgreSQL)
   - Migrate PostgreSQL installation and configuration
   - Migrate Python environment setup
   - Migrate application deployment and service configuration

### Assumptions

1. The target environment will continue to be Fedora-based systems (specifically Fedora 42 as indicated in the Vagrantfile).
2. Self-signed certificates are acceptable for development; production may require integration with a certificate authority.
3. The security requirements (fail2ban, ufw, SSH hardening) will remain the same in the migrated environment.
4. The FastAPI application source code will continue to be available at the specified Git repository.
5. The current plaintext secrets management approach will be replaced with Ansible Vault or another secure secrets management solution.
6. The current directory structure with static HTML files for each site will be preserved.
7. The Redis and Memcached configurations are relatively simple and don't have extensive custom configurations beyond what's visible in the recipes.