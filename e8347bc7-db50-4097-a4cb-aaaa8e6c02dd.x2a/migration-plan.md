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
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw), custom Nginx configuration

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, log directory management

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Manages cookbook dependencies - will be replaced by Ansible Galaxy requirements.yml
- `solo.json`: Contains node attributes and run list - will be replaced by Ansible inventory variables
- `solo.rb`: Chef configuration file - will be replaced by ansible.cfg
- `Vagrantfile`: Defines the development VM - can be adapted for Ansible testing
- `vagrant-provision.sh`: Provisioning script - will be replaced by Ansible playbook

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or local development environment

## Migration Approach

### Key Dependencies to Address

- **nginx (v12.0)**: Replace with Ansible community.general.nginx_* modules or geerlingguy.nginx role
- **memcached (v6.0)**: Replace with geerlingguy.memcached role
- **redisio (v7.2.4)**: Replace with geerlingguy.redis role or community.general.redis_* modules

### Security Considerations

- **Firewall Configuration**: The Chef cookbook configures UFW - migrate to ansible.posix.firewalld for Fedora
- **Fail2ban Setup**: Convert fail2ban configuration to use community.general.fail2ban_* modules
- **SSH Hardening**: Migrate SSH security settings using ansible.posix.sshd_config module
- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook
  - SSL certificates are generated on the fly
  - Recommendation: Use Ansible Vault for all credentials

### Technical Challenges

- **SSL Certificate Generation**: The current setup generates self-signed certificates. Consider using community.crypto modules for certificate management or integrating with Let's Encrypt via geerlingguy.certbot
- **Multi-site Configuration**: The dynamic generation of multiple Nginx sites will require careful templating in Ansible
- **System Tuning**: Security-related sysctl settings will need to be migrated using ansible.posix.sysctl module
- **Service Dependencies**: Ensuring proper ordering of service deployments (e.g., PostgreSQL before FastAPI application)

### Migration Order

1. **cache role** (low complexity, minimal dependencies)
   - Implement Memcached configuration
   - Implement Redis with authentication

2. **nginx-multisite role** (moderate complexity)
   - Implement base Nginx configuration
   - Implement security hardening (fail2ban, firewall)
   - Implement SSL certificate generation
   - Implement virtual host configuration

3. **fastapi-tutorial role** (higher complexity, depends on PostgreSQL)
   - Implement PostgreSQL database setup
   - Implement Python environment configuration
   - Implement application deployment
   - Implement systemd service configuration

### Assumptions

1. The target environment will continue to be Fedora-based systems
2. Self-signed certificates are acceptable for the migrated solution
3. The same security hardening measures are required in the Ansible implementation
4. The FastAPI application source repository will remain available at the same URL
5. The directory structure for web content and SSL certificates can remain the same
6. No additional monitoring or logging requirements beyond what's in the current Chef implementation
7. Redis and Memcached configurations can use community-maintained roles rather than custom implementations