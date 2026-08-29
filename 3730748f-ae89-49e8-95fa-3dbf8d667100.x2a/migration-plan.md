# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with FastAPI application backend and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1 week
- Documentation and Knowledge Transfer: 1 week
- Total: 5-6 weeks

**Complexity Assessment:** Medium
- The repository has a clear structure with well-defined cookbooks
- No custom resources or complex Chef-specific patterns
- Standard infrastructure components (Nginx, FastAPI, PostgreSQL, Redis, Memcached)
- Security configurations that need careful migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled subdomains, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, UFW firewall), custom Nginx configuration templates

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

- `Berksfile`: Defines cookbook dependencies (nginx, memcached, redisio) - will be replaced with Ansible Galaxy requirements.yml
- `solo.json`: Contains node configuration and attributes - will be converted to Ansible group_vars or host_vars
- `solo.rb`: Chef configuration file - not needed in Ansible
- `Vagrantfile`: VM configuration for testing - can be adapted for Ansible testing
- `vagrant-provision.sh`: Provisioning script - will be replaced with Ansible playbook calls

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be designed for local VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role from Galaxy or custom role
- **memcached (~> 6.0)**: Replace with Ansible memcached role from Galaxy or custom role
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role from Galaxy or custom role

### Security Considerations

- **SSL Certificate Management**: The current implementation generates self-signed certificates. Migrate to Ansible's openssl_* modules or certbot role for Let's Encrypt integration.
- **Firewall Configuration**: UFW configuration should be migrated to Ansible's ufw module.
- **Fail2ban Setup**: Migrate fail2ban configuration to Ansible's template module with equivalent templates.
- **SSH Hardening**: SSH security settings should be migrated using Ansible's lineinfile or template modules.
- **Vault/secrets management**:
  - Redis password in cache cookbook: "redis_secure_password_123" - should be stored in Ansible Vault
  - PostgreSQL database credentials in fastapi-tutorial cookbook: "fastapi:fastapi_password" - should be stored in Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of site configurations based on node attributes will need careful migration to Ansible's template system with proper variable structures.
- **Service Dependencies**: Ensuring proper ordering of service installations and configurations (e.g., PostgreSQL before FastAPI application).
- **SSL Certificate Generation**: The self-signed certificate generation logic needs to be replicated in Ansible.
- **Security Hardening**: Comprehensive security configurations need careful migration to maintain the same level of protection.

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for web services)
   - Start with basic Nginx installation and configuration
   - Add SSL certificate generation
   - Implement security hardening (fail2ban, UFW)
   - Configure multi-site setup

2. **cache** (low complexity, independent service)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Set up PostgreSQL database
   - Deploy FastAPI application
   - Configure systemd service

### Assumptions

1. The target environment will continue to be Fedora-based systems (specifically Fedora 42 as indicated in the Vagrantfile).
2. Self-signed certificates are acceptable for the migrated solution (production environments might require proper CA-signed certificates).
3. The security hardening requirements will remain the same (fail2ban, UFW, SSH hardening).
4. The current directory structure in the target environment (/opt/server/*, /var/www/*) should be maintained.
5. The PostgreSQL and Redis passwords currently hardcoded will be moved to Ansible Vault in the migrated solution.
6. The FastAPI application will continue to be deployed from the same Git repository.
7. The Vagrant testing environment will be maintained but updated to use Ansible provisioning.
8. No additional monitoring or logging requirements beyond what's in the current Chef implementation.