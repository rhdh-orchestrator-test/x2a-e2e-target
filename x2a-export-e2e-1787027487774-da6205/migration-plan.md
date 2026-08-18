# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with FastAPI application and caching services. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The complexity is moderate, with security configurations, SSL certificate management, and application deployment requiring careful attention. Estimated timeline: 2-3 weeks for a complete migration with testing.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, UFW firewall), sysctl security settings

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies from Chef Supermarket (nginx, memcached, redisio) and local cookbooks. Migration will require identifying equivalent Ansible Galaxy roles or creating custom roles.
- `solo.json`: Contains the run list and configuration data for Chef Solo. Will be converted to Ansible inventory variables and group_vars.
- `solo.rb`: Chef Solo configuration file. Will be replaced by Ansible configuration.
- `Vagrantfile`: Defines the development VM using Fedora 42. Can be adapted for Ansible testing with minimal changes.
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef. Will be replaced with Ansible provisioning.

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` module or community.general collection
- **memcached (~> 6.0)**: Replace with Ansible memcached role from Galaxy or custom role
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role from Galaxy or custom role
- **PostgreSQL**: Replace with Ansible's `postgresql_*` modules or community.postgresql collection

### Security Considerations

- **SSL Certificate Management**: The current implementation generates self-signed certificates. Migration should maintain this capability while allowing for future integration with Let's Encrypt.
  - Migration approach: Use Ansible's `openssl_*` modules for certificate generation
  
- **Firewall Configuration**: UFW firewall rules are configured for SSH, HTTP, and HTTPS.
  - Migration approach: Use Ansible's `ufw` module or `firewalld` module depending on target OS

- **SSH Hardening**: SSH configuration disables root login and password authentication.
  - Migration approach: Use Ansible's `lineinfile` module or dedicated SSH role

- **fail2ban Configuration**: Brute force protection is implemented.
  - Migration approach: Use Ansible's `template` module with fail2ban configuration templates

- **Vault/secrets management**:
  - Redis password in cache cookbook: Use Ansible Vault for secure storage
  - PostgreSQL credentials in fastapi-tutorial cookbook: Use Ansible Vault for secure storage
  - SSL private keys: Ensure proper permissions and ownership are maintained

### Technical Challenges

- **Multi-site Nginx Configuration**: The current implementation uses Chef templates to generate site configurations dynamically based on node attributes.
  - Mitigation: Create Ansible templates with similar logic, using host_vars or group_vars for site configuration

- **SSL Certificate Generation**: Self-signed certificates are generated for each site.
  - Mitigation: Use Ansible's `openssl_certificate` module with proper idempotency checks

- **Redis Configuration Hack**: The current implementation includes a Ruby block to modify Redis configuration files after they're created.
  - Mitigation: Create a custom Redis configuration template or use Ansible's `lineinfile` module to make specific changes

- **Python Application Deployment**: The FastAPI application is deployed from Git with virtual environment setup.
  - Mitigation: Use Ansible's `git`, `pip`, and `template` modules to replicate the deployment process

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Start with basic Nginx installation and configuration
   - Add SSL certificate generation
   - Implement security hardening (fail2ban, UFW)
   - Configure virtual hosts

2. **cache** (low complexity, standalone service)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Set up PostgreSQL database
   - Deploy Python application from Git
   - Configure systemd service

### Assumptions

1. The target environment will continue to be Fedora-based systems, with potential support for Ubuntu and CentOS as indicated in the cookbook metadata.
2. Self-signed SSL certificates are acceptable for the migrated solution, rather than requiring integration with a certificate authority.
3. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available and compatible.
4. The current security configurations (fail2ban, UFW, SSH hardening) are appropriate for the target environment.
5. The Vagrant development environment will continue to be used for testing the Ansible playbooks.
6. No additional monitoring or logging solutions need to be integrated beyond what's currently configured.
7. The Redis configuration hack is necessary due to compatibility issues with the Redis version and may need to be maintained in the Ansible implementation.
8. The current directory structure for web content (/var/www/[site]) and application (/opt/fastapi-tutorial) should be preserved.