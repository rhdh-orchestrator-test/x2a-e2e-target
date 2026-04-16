# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure for deploying a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three primary cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- Well-structured Chef cookbooks with clear separation of concerns
- Standard infrastructure components (Nginx, Redis, Memcached, PostgreSQL)
- Some security configurations that need careful migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and custom configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw firewall)

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository deployment, Python virtual environment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies (nginx, ssl_certificate, memcached, redisio) - will be replaced by Ansible Galaxy requirements.yml
- `Policyfile.rb`: Defines the run list and cookbook versions - will be replaced by Ansible playbook structure
- `solo.json`: Contains node attributes and configuration data - will be migrated to Ansible inventory variables
- `solo.rb`: Chef Solo configuration - not needed in Ansible
- `Vagrantfile`: Development environment configuration - can be adapted for Ansible testing
- `vagrant-provision.sh`: Provisioning script for Vagrant - will be replaced by Ansible provisioning in Vagrant

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role from Galaxy or custom role
- **ssl_certificate (~> 2.1)**: Replace with Ansible modules for SSL certificate management (openssl_*)
- **memcached (~> 6.0)**: Replace with Ansible memcached role from Galaxy or custom role
- **redisio (~> 7.2.4)**: Replace with Ansible redis role from Galaxy or custom role

### Security Considerations

- **SSL Certificate Management**: The current implementation generates self-signed certificates. Migrate to Ansible's openssl_* modules for certificate generation or consider integrating with Let's Encrypt via certbot.
- **Firewall Configuration**: UFW firewall rules need to be migrated to Ansible's ufw module.
- **Fail2ban Configuration**: Migrate fail2ban configuration to Ansible's template module.
- **SSH Hardening**: SSH security configurations (disabling root login, password authentication) should be migrated to Ansible's lineinfile or template modules.
- **Vault/secrets management**:
  - Redis password in cache cookbook: "redis_secure_password_123" (hardcoded in recipe)
  - PostgreSQL password in fastapi-tutorial cookbook: "fastapi_password" (hardcoded in recipe)
  - Consider using Ansible Vault for these credentials

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of Nginx site configurations based on node attributes will need careful migration to Ansible templates and variables.
- **Redis Configuration Hack**: The Chef cookbook includes a hack to modify Redis configuration files after installation. This will need a clean implementation in Ansible.
- **Service Dependencies**: Ensuring proper service dependencies and restart handlers are maintained in Ansible.
- **PostgreSQL User/Database Creation**: The current implementation uses direct shell commands. This should be migrated to Ansible's postgresql_* modules for better idempotency.

### Migration Order

1. **nginx-multisite** (Priority 1): Core infrastructure component that other services depend on
   - Create base Nginx role
   - Implement SSL certificate generation
   - Configure virtual hosts
   - Implement security hardening (fail2ban, ufw)

2. **cache** (Priority 2): Supporting services
   - Create Memcached role
   - Create Redis role with authentication

3. **fastapi-tutorial** (Priority 3): Application layer
   - Create PostgreSQL role
   - Create Python application deployment role
   - Configure systemd service

### Assumptions

1. The target environment will continue to be Fedora-based systems (the current Vagrantfile specifies Fedora 42).
2. Self-signed certificates are acceptable for development/testing, but production may require proper certificates.
3. The security requirements (fail2ban, ufw, SSH hardening) will remain the same in the Ansible implementation.
4. The FastAPI application source will continue to be pulled from the same Git repository.
5. The current Redis and Memcached configurations are sufficient for the application needs.
6. The PostgreSQL database schema is managed by the FastAPI application and doesn't require additional migration steps.
7. The current directory structure in the target system (/opt/server/*, /var/www/*) should be maintained.
8. The current network configuration (ports, IP addresses) will remain the same.