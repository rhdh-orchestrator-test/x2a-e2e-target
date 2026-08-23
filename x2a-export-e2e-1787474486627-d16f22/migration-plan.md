# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with FastAPI application and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated timeline for migration is 2-3 weeks, with moderate complexity due to the SSL configuration, security hardening, and application deployment requirements.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and custom configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Self-signed SSL certificates, fail2ban integration, UFW firewall configuration, multiple virtual hosts

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository deployment, Python virtual environment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks. Lists both local and external dependencies with version constraints.
- `solo.json`: Chef configuration file that defines the run list and node attributes.
- `solo.rb`: Chef configuration file for Chef Solo.
- `Vagrantfile`: Defines the development environment using Vagrant with Fedora 42.
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef.

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.nginx collection
- **memcached (~> 6.0)**: Replace with Ansible memcached role or community.general.memcached module
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or community.redis collection

### Security Considerations

- **SSL Certificate Management**: The current implementation generates self-signed certificates. Migration should maintain this capability while allowing for future integration with Let's Encrypt.
  - Migration approach: Use Ansible's openssl_* modules for certificate generation

- **Firewall Configuration**: UFW is configured with specific rules for SSH, HTTP, and HTTPS.
  - Migration approach: Use Ansible's ufw module to configure identical rules

- **SSH Hardening**: SSH configuration disables root login and password authentication.
  - Migration approach: Use Ansible's template module with equivalent configuration

- **Fail2ban Integration**: Fail2ban is installed and configured for intrusion prevention.
  - Migration approach: Use Ansible's package and template modules to configure fail2ban

- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook (redis_secure_password_123)
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook (fastapi/fastapi_password)
  - Migration should use Ansible Vault to secure these credentials

### Technical Challenges

- **Multi-site Configuration**: The nginx-multisite cookbook manages multiple virtual hosts with different configurations. This will require careful templating in Ansible.
  - Mitigation: Create a flexible Ansible role that can handle multiple site configurations using variables

- **Application Deployment**: The FastAPI application deployment involves multiple steps including git clone, virtual environment setup, and systemd service configuration.
  - Mitigation: Break down the deployment into discrete tasks with proper handlers and notifications

- **SSL Certificate Management**: Self-signed certificates are generated for each virtual host.
  - Mitigation: Use Ansible's openssl_* modules with proper conditionals to check for existing certificates

### Migration Order

1. **cache** (low risk, moderate value): Start with the cache cookbook as it has the simplest configuration and fewer dependencies.
2. **nginx-multisite** (moderate complexity, high value): Next, migrate the nginx configuration as it's a core component.
3. **fastapi-tutorial** (high complexity, depends on others): Finally, migrate the application deployment which depends on both nginx and potentially the cache services.

### Assumptions

1. The target environment will continue to be Fedora-based systems (specifically Fedora 42 as indicated in the Vagrantfile).
2. Self-signed certificates are acceptable for the migrated solution, rather than requiring integration with a certificate authority.
3. The current security configurations (fail2ban, UFW, SSH hardening) are appropriate and should be maintained in the Ansible implementation.
4. The PostgreSQL database will continue to be deployed on the same host as the application.
5. The Redis and Memcached services will be deployed on the same host as specified in the current configuration.
6. The FastAPI application source will continue to be pulled from the same Git repository.
7. The directory structure for web content (/var/www/[site]) and application (/opt/fastapi-tutorial) will be maintained.
8. The systemd service configuration for the FastAPI application will remain largely unchanged.
9. The current hardcoded credentials will be replaced with Ansible Vault secured variables.
10. The Vagrant development environment will be maintained but updated to use Ansible provisioning instead of Chef.