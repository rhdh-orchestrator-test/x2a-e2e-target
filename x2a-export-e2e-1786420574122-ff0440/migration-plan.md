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
- No custom resources or complex Chef-specific patterns
- Standard infrastructure components (Nginx, FastAPI, PostgreSQL, Redis, Memcached)
- Security configurations that need careful migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and self-signed certificates
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, UFW firewall), sysctl security settings

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

- **cache**:
    - Description: Configures caching services (Memcached and Redis) with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, log directory management

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies (nginx, memcached, redisio)
- `solo.json`: Chef configuration with run list and node attributes
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Defines development VM using Fedora 42
- `vagrant-provision.sh`: Shell script to provision the VM with Chef

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile) with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` role or direct package installation and configuration
- **memcached (~> 6.0)**: Replace with Ansible's `geerlingguy.memcached` role or direct package management
- **redisio (~> 7.2.4)**: Replace with Ansible's `geerlingguy.redis` role or direct package management

### Security Considerations

- **Firewall Configuration**: UFW rules need to be migrated to equivalent Ansible UFW module tasks
- **fail2ban Setup**: Configuration needs to be migrated to Ansible tasks
- **SSH Hardening**: SSH configuration (disable root login, password authentication) needs careful migration
- **SSL Certificates**: Self-signed certificate generation needs to be implemented in Ansible
- **Vault/secrets management**:
  - Redis password in cache cookbook: `redis_secure_password_123`
  - PostgreSQL credentials in fastapi-tutorial cookbook: `fastapi:fastapi_password`
  - These should be migrated to Ansible Vault

### Technical Challenges

- **Multi-site Configuration**: Ensuring the dynamic generation of Nginx site configurations works correctly in Ansible
- **SSL Certificate Management**: Properly handling SSL certificate generation and permissions
- **Service Dependencies**: Ensuring proper ordering of service installations and configurations
- **Idempotency**: Ensuring all operations remain idempotent, especially the database user creation and SSL certificate generation

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Contains security configurations that should be established first

2. **cache** (Priority 2)
   - Supporting service with external dependencies
   - Moderate complexity with Redis authentication

3. **fastapi-tutorial** (Priority 3)
   - Application deployment that depends on other infrastructure components
   - Contains database setup and application configuration

### Assumptions

1. The target environment will continue to be Fedora 42 or compatible Linux distributions
2. Self-signed certificates are acceptable for the migrated solution (not using Let's Encrypt or other CA)
3. The same security policies should be maintained in the Ansible implementation
4. The Vagrant development workflow should be preserved but updated for Ansible
5. No changes to the application code or database schema are required
6. The current directory structure with multiple sites will be maintained
7. The PostgreSQL and Redis passwords are development credentials and will be replaced in production

## Ansible Structure Recommendation

```
ansible/
├── inventories/
│   ├── development/
│   │   ├── group_vars/
│   │   │   └── all.yml  # Development variables
│   │   └── hosts        # Development inventory
│   └── production/
│       ├── group_vars/
│       │   └── all.yml  # Production variables
│       └── hosts        # Production inventory
├── roles/
│   ├── nginx_multisite/
│   │   ├── defaults/
│   │   ├── files/
│   │   ├── handlers/
│   │   ├── tasks/
│   │   ├── templates/
│   │   └── vars/
│   ├── fastapi_app/
│   │   └── ...
│   └── cache_services/
│       └── ...
├── playbooks/
│   ├── site.yml         # Main playbook
│   ├── nginx.yml        # Individual component playbooks
│   ├── cache.yml
│   └── fastapi.yml
└── Vagrantfile          # Updated for Ansible provisioning
```

## Migration Testing Strategy

1. Create Ansible roles and playbooks in parallel with existing Chef setup
2. Use Vagrant to create test VMs for both Chef and Ansible provisioning
3. Compare the resulting configurations and services
4. Develop automated tests to verify functionality
5. Document any differences or improvements in the Ansible implementation