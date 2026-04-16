# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure for deploying a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application with PostgreSQL. The migration to Ansible will involve converting three primary Chef cookbooks to Ansible roles, addressing external dependencies, and ensuring security configurations are properly maintained.

**Estimated Timeline:** 3-4 weeks
**Complexity:** Medium
**Team Size Recommendation:** 2-3 DevOps engineers

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled subdomains, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw), sysctl security settings

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks - will be replaced by Ansible Galaxy requirements.yml
- `Policyfile.rb`: Chef policy configuration - will be replaced by Ansible playbook structure
- `Vagrantfile`: VM configuration for development/testing - can be adapted for Ansible testing
- `solo.json`: Chef node configuration - will be replaced by Ansible inventory variables
- `solo.rb`: Chef configuration - will be replaced by ansible.cfg
- `vagrant-provision.sh`: Provisioning script for Vagrant - will be replaced by Ansible provisioning

### Target Details

Based on the source configuration files:

- **Operating System**: 
  - Primary: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports statements)
  - Development: Fedora 42 (based on Vagrant configuration)
- **Virtual Machine Technology**: Libvirt (based on Vagrant provider configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or direct package installation
- **ssl_certificate (~> 2.1)**: Replace with Ansible certificate management modules (openssl_*)
- **memcached (~> 6.0)**: Replace with Ansible memcached role or direct package configuration
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or direct package configuration

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for development
  - Migration should maintain proper certificate permissions (640) and ownership (root:ssl-cert)
  - Consider integrating with Ansible Vault for certificate storage

- **Firewall Configuration**: 
  - UFW firewall rules need to be migrated to Ansible ufw module
  - Default deny policy with specific allows for SSH, HTTP, HTTPS

- **SSH Hardening**:
  - Disable root login
  - Disable password authentication
  - Maintain these security settings in Ansible

- **System Hardening**:
  - sysctl security settings need to be migrated
  - fail2ban configuration needs to be preserved

- **Vault/secrets management**:
  - Redis password in cache cookbook: "redis_secure_password_123"
  - PostgreSQL database credentials in fastapi-tutorial cookbook: "fastapi:fastapi_password"
  - Total credentials detected: 2 hardcoded passwords

### Technical Challenges

- **Multi-site Configuration**: The dynamic generation of multiple Nginx sites will need careful translation to Ansible templates and loops
- **SSL Certificate Generation**: Self-signed certificate generation logic needs to be preserved with proper file permissions
- **Security Hardening**: Comprehensive security configurations need to be maintained across firewall, SSH, and system settings
- **Service Dependencies**: Proper ordering of service installations and configurations must be maintained (e.g., PostgreSQL before FastAPI application)

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Start with basic Nginx installation and configuration
   - Add SSL certificate management
   - Add security hardening features
   - Implement multi-site configuration

2. **cache** (Priority 2)
   - Implement Memcached configuration
   - Implement Redis with authentication
   - Ensure proper service management

3. **fastapi-tutorial** (Priority 3)
   - Set up PostgreSQL database
   - Configure Python environment and application deployment
   - Set up systemd service

### Assumptions

1. The target environment will continue to be Linux-based (Ubuntu/CentOS/Fedora)
2. Self-signed certificates are acceptable for development (production would likely use different certificate sources)
3. The same network configuration and port mappings will be maintained
4. The FastAPI application source will continue to be available at the specified Git repository
5. The current security configurations are appropriate for the target environment
6. Redis and Memcached configurations don't require significant customization beyond what's currently implemented
7. The PostgreSQL database schema is managed by the FastAPI application and doesn't require additional migration steps

## Ansible Structure Recommendation

```
ansible-nginx-multisite/
├── ansible.cfg
├── inventory/
│   ├── group_vars/
│   │   ├── all.yml
│   │   └── webservers.yml
│   └── hosts.ini
├── playbooks/
│   ├── site.yml
│   ├── nginx.yml
│   ├── cache.yml
│   └── fastapi.yml
├── roles/
│   ├── nginx-multisite/
│   │   ├── defaults/
│   │   ├── handlers/
│   │   ├── tasks/
│   │   └── templates/
│   ├── cache/
│   │   ├── defaults/
│   │   ├── handlers/
│   │   ├── tasks/
│   │   └── templates/
│   └── fastapi-tutorial/
│       ├── defaults/
│       ├── handlers/
│       ├── tasks/
│       └── templates/
└── requirements.yml
```

## Testing Strategy

1. Develop and test each role individually using Molecule
2. Create a Vagrant-based test environment similar to the current setup
3. Implement integration tests to verify the complete stack works together
4. Compare the results with the current Chef implementation to ensure feature parity