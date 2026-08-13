# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with FastAPI application and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated timeline for this migration is 2-3 weeks, with moderate complexity due to the security configurations and SSL certificate management.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw, sysctl)

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

- `Berksfile`: Defines cookbook dependencies (nginx, memcached, redisio) - will be replaced by Ansible Galaxy requirements.yml
- `solo.json`: Contains node configuration and attributes - will be converted to Ansible group_vars or host_vars
- `solo.rb`: Chef configuration file - not needed in Ansible
- `Vagrantfile`: Defines the development VM - will need updating to use Ansible provisioner
- `vagrant-provision.sh`: Shell script for Chef provisioning - will be replaced by Ansible playbook calls

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be a local development environment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks with custom configuration

### Security Considerations

- **Firewall Configuration**: The Chef cookbook configures UFW - migrate to Ansible's `ufw` module
- **Fail2ban Setup**: Migrate fail2ban configuration to Ansible tasks using templates
- **SSH Hardening**: Migrate SSH security settings (disable root login, password authentication) to Ansible tasks
- **SSL Certificate Management**: The cookbook generates self-signed certificates - use Ansible's `openssl_*` modules
- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook (`fastapi:fastapi_password`)
  - Consider using Ansible Vault for these credentials

### Technical Challenges

- **SSL Certificate Generation**: The current setup generates self-signed certificates for each site. Ansible will need to replicate this with the `openssl_certificate` module.
- **Multi-site Configuration**: The Nginx configuration supports multiple sites with different document roots and SSL settings. This will require careful template conversion.
- **Security Hardening**: The security.rb recipe includes multiple security measures that need to be carefully migrated to maintain the same level of protection.
- **Service Dependencies**: The FastAPI application depends on PostgreSQL, and the services have specific ordering requirements that need to be maintained in Ansible.

### Migration Order

1. **nginx-multisite cookbook** (Priority 1)
   - This forms the foundation of the infrastructure and other components depend on it
   - Start with basic Nginx configuration, then add SSL and security features

2. **cache cookbook** (Priority 2)
   - Relatively standalone with external dependencies on memcached and redis
   - Moderate complexity due to Redis authentication configuration

3. **fastapi-tutorial cookbook** (Priority 3)
   - Depends on a properly configured web server
   - Involves database setup, application deployment, and service configuration

### Assumptions

1. The target environment will continue to be Fedora-based systems (Fedora 42 as specified in the Vagrantfile)
2. The self-signed certificates approach is acceptable for the migrated solution (vs. using Let's Encrypt or other CA)
3. The current security configurations (fail2ban, ufw, SSH hardening) are required in the migrated solution
4. The directory structure for document roots and SSL certificates will remain the same
5. PostgreSQL and Python versions will remain compatible with the FastAPI application
6. The Redis and Memcached configurations don't have specific tuning requirements beyond what's in the current cookbooks
7. The Vagrant development environment will be maintained, just switching from Chef to Ansible provisioning