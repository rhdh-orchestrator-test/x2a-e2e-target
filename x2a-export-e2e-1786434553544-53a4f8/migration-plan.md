# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server setup with FastAPI application backend and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- Moderate number of external dependencies
- Security configurations that need careful migration
- Self-signed SSL certificates that need to be managed

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
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Manages cookbook dependencies - will be replaced by Ansible Galaxy requirements.yml
- `solo.json`: Contains node configuration and attributes - will be replaced by Ansible inventory variables
- `solo.rb`: Chef configuration file - will be replaced by ansible.cfg
- `Vagrantfile`: Defines development VM - can be adapted for Ansible testing
- `vagrant-provision.sh`: Provisioning script - will be replaced by Ansible playbook

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu (18.04+) and CentOS (7+) mentioned in cookbook metadata
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible community.nginx collection or direct package installation
- **memcached (~> 6.0)**: Replace with Ansible community.general.memcached module
- **redisio (~> 7.2.4)**: Replace with Ansible community.redis collection or direct package installation

### Security Considerations

- **Firewall Configuration**: The current setup uses UFW - migrate to Ansible's community.general.ufw module
- **Fail2ban Configuration**: Migrate fail2ban configuration to Ansible community.general.fail2ban module
- **SSH Hardening**: Migrate SSH security settings using Ansible's openssh_config module
- **Sysctl Security Settings**: Migrate using Ansible's community.general.sysctl module
- **Vault/secrets management**:
  - Redis password in cache cookbook (plaintext): Should be migrated to Ansible Vault
  - PostgreSQL credentials in fastapi-tutorial cookbook (plaintext): Should be migrated to Ansible Vault
  - SSL private keys: Ensure proper permissions are maintained during migration

### Technical Challenges

- **SSL Certificate Generation**: The current setup generates self-signed certificates. Ansible has modules for this, but the workflow needs careful migration.
- **Multi-site Configuration**: The dynamic generation of multiple Nginx sites needs to be preserved in Ansible using loops and templates.
- **Service Dependencies**: The FastAPI application depends on PostgreSQL, and the proper startup order needs to be maintained.
- **Redis Configuration Hack**: The current setup includes a ruby_block to modify Redis configuration files after installation. This needs a clean Ansible equivalent.

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Start with basic Nginx installation and configuration
   - Then add SSL certificate generation
   - Finally add security hardening features

2. **cache** (Priority 2)
   - Memcached and Redis services
   - Ensure proper configuration and security

3. **fastapi-tutorial** (Priority 3)
   - Application deployment with database
   - Depends on proper infrastructure setup

### Assumptions

1. The target environment will continue to be Fedora/CentOS/Ubuntu based systems
2. Self-signed certificates are acceptable for the migrated solution (not using Let's Encrypt or other CA)
3. The same security policies should be applied in the Ansible version
4. The Vagrant development workflow should be preserved
5. The current plaintext secrets in the Chef recipes will be migrated to Ansible Vault
6. The PostgreSQL database setup for FastAPI will remain similar
7. The multi-site configuration pattern will be maintained