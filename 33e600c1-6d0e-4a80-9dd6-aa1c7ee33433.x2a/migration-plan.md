# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 3 weeks
- Testing and Validation: 2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 7 weeks

**Complexity Assessment:** Medium
- The codebase is well-structured with clear separation of concerns
- Security configurations are present and need careful migration
- Multiple external dependencies need to be addressed

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled subdomains, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening with fail2ban and UFW

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks, lists both local and external dependencies
- `Policyfile.rb`: Chef policy file defining the run list and cookbook dependencies
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings
- `solo.json`: Node attributes and run list for Chef Solo
- `Vagrantfile`: Defines a Fedora 42 VM for development and testing
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef

### Target Details

- **Operating System**: Fedora 42 (primary) with support for Ubuntu 18.04+ and CentOS 7+ based on cookbook metadata
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible Galaxy role `geerlingguy.nginx` or create a custom Nginx role
- **memcached (~> 6.0)**: Replace with Ansible Galaxy role `geerlingguy.memcached`
- **redisio (~> 7.2.4)**: Replace with Ansible Galaxy role `geerlingguy.redis` or DavidWittman.redis
- **ssl_certificate (~> 2.1)**: Replace with Ansible's `openssl_*` modules for certificate management

### Security Considerations

- **fail2ban configuration**: Migrate using Ansible's package and template modules to configure fail2ban
- **UFW firewall rules**: Use Ansible's `ufw` module to configure firewall rules
- **SSH hardening**: Use Ansible's `lineinfile` or template module to configure SSH security settings
- **SSL certificates**: Use Ansible's `openssl_*` modules for certificate generation and management
- **Redis password**: Store in Ansible Vault and reference in templates
- **PostgreSQL credentials**: Store database credentials in Ansible Vault

### Technical Challenges

- **Multi-site Nginx configuration**: Create Ansible templates for site configurations with proper variable substitution
- **SSL certificate generation**: Implement equivalent self-signed certificate generation logic using Ansible's `openssl_*` modules
- **Service dependencies**: Ensure proper ordering of tasks for services that depend on each other (e.g., PostgreSQL before FastAPI)
- **Python environment setup**: Create idempotent tasks for virtual environment creation and dependency installation

### Migration Order

1. **cache cookbook** (low complexity, foundational service)
   - Implement Memcached configuration
   - Implement Redis configuration with authentication

2. **nginx-multisite cookbook** (medium complexity, depends on SSL certificates)
   - Implement basic Nginx configuration
   - Implement SSL certificate generation
   - Implement site configuration templates
   - Implement security hardening (fail2ban, UFW)

3. **fastapi-tutorial cookbook** (high complexity, depends on PostgreSQL)
   - Implement PostgreSQL installation and configuration
   - Implement Python environment setup
   - Implement application deployment
   - Implement systemd service configuration

### Assumptions

1. The target environment will continue to be Fedora 42 or compatible Linux distributions
2. Self-signed certificates are acceptable for development/testing (production would likely use Let's Encrypt or other CA)
3. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
4. The current security configurations (fail2ban, UFW, SSH hardening) are appropriate for the target environment
5. Redis and PostgreSQL passwords in the Chef code are development/testing passwords and will be replaced with secure passwords in Ansible Vault
6. The Vagrant development environment will be maintained for testing the Ansible playbooks

## Ansible Structure Recommendation

```
ansible-nginx-multisite/
├── inventories/
│   ├── development/
│   │   ├── hosts.yml
│   │   └── group_vars/
│   └── production/
│       ├── hosts.yml
│       └── group_vars/
├── roles/
│   ├── nginx_multisite/
│   ├── cache/
│   └── fastapi_app/
├── playbooks/
│   ├── site.yml
│   ├── nginx.yml
│   ├── cache.yml
│   └── fastapi.yml
├── requirements.yml  # For Ansible Galaxy dependencies
└── Vagrantfile       # For local testing
```

## Testing Strategy

1. Create a Vagrant environment similar to the current one for local testing
2. Develop and test each role individually
3. Integrate roles and test the complete playbook
4. Verify functionality against the original Chef implementation
5. Document any differences or improvements

## Knowledge Transfer Plan

1. Document each Ansible role with README files explaining purpose and configuration options
2. Create example inventory files with commented variables
3. Provide a migration summary document highlighting key differences between the Chef and Ansible implementations
4. Schedule knowledge transfer sessions with the team