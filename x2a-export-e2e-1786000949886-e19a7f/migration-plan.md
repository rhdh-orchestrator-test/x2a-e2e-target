# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with FastAPI application backend and caching services. The migration to Ansible will involve converting three Chef cookbooks with their dependencies, templates, and configuration files. The estimated complexity is moderate, with an estimated timeline of 2-3 weeks for a complete migration.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures nginx with multiple SSL-enabled subdomains, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site virtual hosts, SSL certificate generation, fail2ban integration, UFW firewall configuration, security hardening

- **fastapi-tutorial**:
    - Description: Configures FastAPI tutorial application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

- **cache**:
    - Description: Configures caching services (memcached and redis) with security settings
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, log directory management

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies for Chef Berkshelf - will be replaced with Ansible Galaxy requirements.yml
- `solo.json`: Defines the Chef run list and configuration attributes - will be replaced with Ansible inventory variables
- `solo.rb`: Chef Solo configuration - will be replaced with ansible.cfg
- `Vagrantfile`: Defines the development VM - can be adapted for Ansible testing
- `vagrant-provision.sh`: Provisions the VM with Chef - will be replaced with Ansible provisioning

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (from Vagrantfile) with support for Ubuntu 18.04+ and CentOS 7+ (from cookbook metadata)
- **Virtual Machine Technology**: Libvirt (from Vagrantfile)
- **Cloud Platform**: Not specified, appears to be targeting on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks

### Security Considerations

- **SSL Certificate Management**: The current setup generates self-signed certificates. Migration should maintain this capability or integrate with Let's Encrypt.
  - Migration approach: Use Ansible's `community.crypto.openssl_*` modules for certificate generation or `community.crypto.acme_certificate` for Let's Encrypt integration.

- **Firewall Configuration**: UFW is configured with specific rules for HTTP, HTTPS, and SSH.
  - Migration approach: Use Ansible's `community.general.ufw` module to maintain the same firewall rules.

- **Fail2ban Integration**: Fail2ban is configured for intrusion prevention.
  - Migration approach: Use Ansible to install and configure fail2ban with similar jail settings.

- **SSH Hardening**: SSH is configured to disable root login and password authentication.
  - Migration approach: Use Ansible's `ansible.posix.sshd_config` module to apply the same security settings.

- **Vault/secrets management**: 
  - Redis password in cache cookbook: "redis_secure_password_123"
  - PostgreSQL database credentials in fastapi-tutorial cookbook: "fastapi:fastapi_password"
  - Migration approach: Use Ansible Vault to securely store these credentials

### Technical Challenges

- **Multi-site Configuration**: The nginx-multisite cookbook manages multiple virtual hosts with dynamic configuration. 
  - Mitigation: Use Ansible templates with loops to generate similar site configurations.

- **Service Orchestration**: The current setup manages service dependencies (e.g., FastAPI depends on PostgreSQL).
  - Mitigation: Use Ansible handlers and meta dependencies to ensure proper service ordering.

- **SSL Certificate Generation**: Self-signed certificates are generated for each site.
  - Mitigation: Use Ansible's crypto modules to generate certificates with similar parameters.

- **Redis Configuration Hack**: The cache cookbook includes a Ruby block to modify Redis configuration.
  - Mitigation: Use Ansible's lineinfile or template module to achieve the same configuration adjustments.

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for web services)
   - Start with basic Nginx installation and configuration
   - Add SSL certificate generation
   - Add security hardening (fail2ban, firewall)
   - Add multi-site configuration

2. **cache** (low complexity, standalone service)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (moderate complexity, depends on PostgreSQL)
   - Implement PostgreSQL installation and configuration
   - Implement Python environment setup
   - Implement application deployment
   - Configure systemd service

### Assumptions

1. The target environment will continue to use Fedora 42 or a compatible Linux distribution.
2. The self-signed SSL certificates are acceptable for the target environment (not production).
3. The current security settings (fail2ban, UFW, SSH hardening) are appropriate for the target environment.
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
5. The current directory structure in the target environment (/opt/fastapi-tutorial, /var/www/*/etc.) will be maintained.
6. The current service names and ports will be maintained.
7. The current database credentials and Redis password are not sensitive and can be migrated as-is.