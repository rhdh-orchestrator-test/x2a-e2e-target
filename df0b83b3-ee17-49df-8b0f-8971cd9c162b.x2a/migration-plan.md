# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The codebase is well-structured with clear separation of concerns
- External dependencies on community cookbooks will need Ansible equivalents
- Security configurations require careful migration to maintain hardening standards

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and custom site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw firewall)

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

- `Berksfile`: Dependency management file listing cookbook dependencies (will be replaced by Ansible requirements.yml)
- `Policyfile.rb`: Chef policy file defining the run list and cookbook versions (will be replaced by Ansible playbook)
- `solo.json`: Configuration data for Chef Solo with site configurations and security settings (will be converted to Ansible variables)
- `solo.rb`: Chef Solo configuration (will be replaced by Ansible configuration)
- `Vagrantfile`: Defines the development VM using Fedora 42 (can be adapted for Ansible testing)
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef (will be replaced by Ansible provisioner)

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with development environment using Fedora 42
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible `geerlingguy.nginx` role or custom Nginx role
- **memcached (~> 6.0)**: Replace with Ansible `geerlingguy.memcached` role
- **redisio (~> 7.2.4)**: Replace with Ansible `geerlingguy.redis` or `DavidWittman.redis` role
- **ssl_certificate (~> 2.1)**: Replace with Ansible `openssl_*` modules for certificate generation

### Security Considerations

- **Firewall (UFW)**: Migrate UFW configuration to Ansible `ufw` module
- **Fail2ban**: Migrate fail2ban configuration to Ansible using `template` module for configuration files
- **SSH Hardening**: Migrate SSH security settings using Ansible `lineinfile` or `template` modules
- **SSL Certificates**: Ensure secure generation and permissions of SSL certificates using Ansible's `openssl_*` modules
- **Redis Authentication**: Maintain Redis password authentication in Ansible configuration
- **PostgreSQL Security**: Ensure secure database user creation and permissions

### Technical Challenges

- **Multi-site Nginx Configuration**: Create a flexible Ansible role that can handle multiple virtual hosts with SSL
- **Self-signed Certificate Generation**: Implement equivalent OpenSSL commands in Ansible for development environments
- **System Hardening**: Ensure all security configurations are properly migrated to maintain security posture
- **Service Dependencies**: Maintain proper ordering of service installation and configuration
- **Idempotency**: Ensure all Ansible tasks are idempotent, especially for database creation and user setup

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Start with basic Nginx installation and configuration
   - Add SSL certificate generation
   - Implement virtual host configuration
   - Add security hardening features

2. **cache** (Priority 2)
   - Implement Memcached configuration
   - Implement Redis with authentication
   - Ensure proper service management

3. **fastapi-tutorial** (Priority 3)
   - Set up PostgreSQL database
   - Implement Python environment setup
   - Configure application deployment from Git
   - Set up systemd service

### Assumptions

1. The target environment will continue to support both Ubuntu and CentOS/RHEL-based distributions
2. The Vagrant development environment will be maintained for testing
3. Self-signed certificates are acceptable for development environments
4. The current security posture must be maintained or improved
5. No changes to the application code or database schema are required
6. The FastAPI application will continue to be deployed from the same Git repository
7. Redis authentication will use the same password mechanism
8. The current directory structure for web content will be preserved
9. The current systemd service configuration for FastAPI will be maintained
10. No additional monitoring or logging requirements beyond what's in the current Chef code

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
│   ├── nginx-multisite/
│   ├── cache/
│   └── fastapi-tutorial/
├── playbooks/
│   ├── site.yml
│   ├── nginx.yml
│   ├── cache.yml
│   └── fastapi.yml
├── requirements.yml
└── Vagrantfile
```

## Testing Strategy

1. Develop and test each role independently using Molecule
2. Create integration tests to verify interactions between components
3. Use the existing Vagrant setup to validate the full stack deployment
4. Compare the results with the current Chef-based deployment to ensure equivalence