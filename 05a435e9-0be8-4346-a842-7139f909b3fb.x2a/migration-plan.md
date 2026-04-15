# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx configuration with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three primary Chef cookbooks to Ansible roles, addressing external dependencies, and ensuring security configurations are properly maintained.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 3 weeks
- Testing and Validation: 2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 7 weeks

**Complexity Assessment:** Medium
- Well-structured Chef cookbooks with clear separation of concerns
- Standard infrastructure components (Nginx, Redis, Memcached, PostgreSQL)
- Security configurations that need careful migration
- Self-contained application deployment

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
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management file listing cookbook dependencies (nginx, ssl_certificate, memcached, redisio)
- `Policyfile.rb`: Chef Policyfile defining the run list and cookbook dependencies
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings
- `solo.json`: Node attributes and run list configuration for Chef Solo
- `Vagrantfile`: Vagrant configuration for local development using Fedora 42
- `vagrant-provision.sh`: Provisioning script for Vagrant that installs Chef and dependencies

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with Fedora 42 used in Vagrant development environment
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile configuration)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or collection (e.g., `ansible.posix.nginx`)
- **ssl_certificate (~> 2.1)**: Replace with Ansible's `community.crypto` collection for certificate management
- **memcached (~> 6.0)**: Replace with Ansible memcached role or direct package installation
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role or direct package installation and configuration

### Security Considerations

- **SSL Certificate Management**: Migration must maintain proper certificate generation and permissions (root:ssl-cert with 640 permissions)
- **Firewall Configuration**: UFW rules must be migrated with equivalent Ansible firewall module
- **Fail2ban Configuration**: Fail2ban setup needs to be migrated with proper jail configurations
- **SSH Hardening**: SSH security settings (disable root login, password authentication) must be preserved
- **Redis Authentication**: Redis password authentication must be maintained
- **PostgreSQL Security**: Database user credentials and permissions must be securely managed

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of site configurations based on attributes needs careful translation to Ansible variables and templates
- **SSL Certificate Generation**: Self-signed certificate generation logic needs to be replicated in Ansible
- **Service Dependencies**: Ensuring proper ordering of service installations and configurations
- **Idempotency**: Ensuring all operations remain idempotent, especially database user creation and application deployment

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Begin with basic Nginx installation
   - Add SSL certificate management
   - Implement security hardening (fail2ban, UFW)
   - Configure multi-site setup

2. **cache** (low complexity, independent service)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, depends on database)
   - Set up PostgreSQL database
   - Configure Python environment
   - Deploy application from Git
   - Configure systemd service

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS/RHEL-based distributions
2. Self-signed certificates are acceptable for development/testing (production would likely use Let's Encrypt or other CA)
3. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
4. The Redis password "redis_secure_password_123" and PostgreSQL password "fastapi_password" are development credentials that should be replaced with secure, environment-specific values in production
5. The current security configurations (fail2ban, UFW, SSH hardening) are appropriate for the target environment
6. The Vagrant development environment will be maintained for testing the Ansible playbooks

## Ansible Structure Recommendation

```
ansible-nginx-multisite/
├── inventory/
│   ├── hosts.yml
│   └── group_vars/
│       ├── all.yml
│       └── webservers.yml
├── roles/
│   ├── nginx-multisite/
│   ├── cache/
│   └── fastapi-tutorial/
├── playbooks/
│   ├── site.yml
│   ├── nginx.yml
│   ├── cache.yml
│   └── fastapi.yml
├── templates/
├── files/
└── vagrant/
    └── Vagrantfile
```

## Implementation Notes

1. Use Ansible Vault for sensitive information (Redis password, PostgreSQL credentials)
2. Implement proper handlers for service restarts to match Chef notifications
3. Use Ansible's template module to replace Chef templates
4. Consider using community-maintained roles for standard components (Nginx, Redis, Memcached)
5. Implement proper tags for selective execution of playbook components
6. Maintain idempotency in all operations, especially database operations
7. Document all variables and their default values
8. Create comprehensive README with usage instructions