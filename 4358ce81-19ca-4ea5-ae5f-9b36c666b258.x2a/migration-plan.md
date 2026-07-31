# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx configuration with FastAPI application and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated timeline for this migration is 2-3 weeks, with moderate complexity due to the security configurations and SSL certificate management.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: SSL certificate generation, security hardening (fail2ban, ufw), multi-site configuration

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks. Lists both local and external cookbook dependencies.
- `solo.json`: Configuration data for Chef Solo, contains site configurations and security settings.
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings.
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef.
- `Vagrantfile`: Defines the development VM configuration using Fedora 42.

### Target Details

Based on the source repository analysis:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0) based on cookbook metadata, but the Vagrantfile uses Fedora 42.
- **Virtual Machine Technology**: Vagrant with libvirt provider (based on Vagrantfile configuration).
- **Cloud Platform**: Not specified, appears to be designed for local development/testing.

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.nginx collection
- **memcached (~> 6.0)**: Replace with Ansible memcached role or community.general.memcached module
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or community.redis collection

### Security Considerations

- **SSL Certificate Management**: The current setup generates self-signed certificates. Migration should maintain this capability or integrate with Let's Encrypt.
  - Migration approach: Use Ansible's openssl_* modules for certificate generation or community.crypto collection.

- **Firewall Configuration**: Uses UFW for firewall management.
  - Migration approach: Use Ansible's ufw module or firewalld module depending on target OS.

- **Fail2ban Configuration**: Configured for intrusion prevention.
  - Migration approach: Use Ansible's template module to configure fail2ban.

- **SSH Hardening**: Disables root login and password authentication.
  - Migration approach: Use Ansible's lineinfile or template module to configure SSH.

- **Vault/secrets management**:
  - Redis password in cache cookbook (plaintext in recipe)
  - PostgreSQL credentials in fastapi-tutorial cookbook (plaintext in recipe)
  - Migration approach: Use Ansible Vault for storing sensitive information

### Technical Challenges

- **Multi-site Nginx Configuration**: The current setup dynamically creates Nginx site configurations based on node attributes.
  - Mitigation: Use Ansible's with_items/loop to iterate through site configurations.

- **SSL Certificate Generation**: Self-signed certificates are generated for each site.
  - Mitigation: Use Ansible's openssl_* modules to generate certificates.

- **Redis Configuration Hack**: The current setup includes a ruby_block to modify Redis configuration.
  - Mitigation: Create a proper Redis configuration template in Ansible.

- **PostgreSQL User/Database Creation**: The current setup uses inline SQL commands.
  - Mitigation: Use Ansible's postgresql_* modules for database management.

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Start with basic Nginx installation
   - Add security configurations
   - Add SSL certificate generation
   - Add site configurations

2. **cache** (low complexity, standalone service)
   - Configure Memcached
   - Configure Redis with authentication

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Set up Python environment
   - Configure PostgreSQL
   - Deploy application
   - Configure systemd service

### Assumptions

1. The target environment will continue to be Vagrant-based for development/testing.
2. Self-signed certificates are acceptable for the migrated solution (not production).
3. The same security hardening measures should be maintained in the Ansible version.
4. The FastAPI application source will continue to be pulled from the same Git repository.
5. The Redis and PostgreSQL passwords in the current implementation are development passwords and will be replaced with Ansible Vault secured variables.
6. The current Chef implementation doesn't use encrypted data bags or other secret management, so all secrets are in plaintext.
7. The Nginx sites configuration in solo.json will be migrated to Ansible group_vars or host_vars.