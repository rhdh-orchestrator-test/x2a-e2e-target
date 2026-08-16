# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their recipes, templates, and files to equivalent Ansible roles and playbooks.

**Scope**: 3 Chef cookbooks with 7 recipes, multiple templates, and static files
**Complexity**: Medium - The configuration is well-structured but includes security hardening, SSL certificate management, and database configuration
**Timeline Estimate**: 2-3 weeks for complete migration, testing, and documentation

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening with fail2ban and UFW, sysctl security settings

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

- `Berksfile`: Chef dependency management file listing cookbook dependencies (nginx, memcached, redisio)
- `solo.json`: Chef node configuration with run list and attribute settings for Nginx sites and security settings
- `solo.rb`: Chef configuration file for Chef Solo
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Vagrant configuration for development environment using Fedora 42

### Target Details

Based on the source configuration files:

- **Operating System**: Supports both Ubuntu (>= 18.04) and CentOS (>= 7.0), with Fedora 42 used in Vagrant development environment
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or nginx_core module
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or package installation tasks with custom configuration

### Security Considerations

- **SSL Certificate Management**: The current setup generates self-signed certificates for development. Migration should maintain this capability while allowing for production certificate integration.
- **Firewall Configuration**: UFW configuration needs to be migrated to equivalent Ansible UFW module tasks.
- **fail2ban Setup**: Configuration needs to be migrated to Ansible tasks for fail2ban installation and configuration.
- **SSH Hardening**: Current configuration disables root login and password authentication based on attributes.
- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook (`redis_secure_password_123`)
  - PostgreSQL database credentials are hardcoded in the fastapi-tutorial cookbook (`fastapi`/`fastapi_password`)
  - These should be migrated to Ansible Vault or another secrets management solution

### Technical Challenges

- **Multi-site Configuration**: The dynamic generation of Nginx site configurations based on node attributes needs to be replicated using Ansible loops and templates.
- **SSL Certificate Generation**: The self-signed certificate generation logic needs to be migrated to equivalent Ansible commands.
- **Service Dependencies**: Ensuring proper ordering of service installation, configuration, and startup in Ansible.
- **PostgreSQL User/Database Creation**: Converting the PostgreSQL user and database creation commands to idempotent Ansible tasks.

### Migration Order

1. **nginx-multisite** (Priority 1): Core infrastructure component that other services depend on
   - Start with basic Nginx installation and configuration
   - Add SSL certificate generation
   - Add virtual host configuration
   - Add security hardening components

2. **cache** (Priority 2): Supporting services
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (Priority 3): Application deployment
   - PostgreSQL installation and configuration
   - Python environment setup
   - Application deployment and service configuration

### Assumptions

1. The target environment will continue to use the same operating systems (Ubuntu/CentOS/Fedora)
2. Self-signed certificates are acceptable for development, but production deployment may require integration with Let's Encrypt or another certificate provider
3. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
4. The current security settings (fail2ban, UFW, SSH hardening) are appropriate for the target environment
5. The Vagrant development environment will be maintained, but Chef provisioning will be replaced with Ansible
6. The Redis and PostgreSQL passwords in the current configuration are development passwords and will be replaced with more secure values in production

## Ansible Structure Recommendation

```
ansible/
├── inventories/
│   ├── development/
│   │   ├── hosts.yml
│   │   └── group_vars/
│   └── production/
│       ├── hosts.yml
│       └── group_vars/
├── roles/
│   ├── nginx_multisite/
│   │   ├── defaults/
│   │   ├── files/
│   │   ├── handlers/
│   │   ├── tasks/
│   │   ├── templates/
│   │   └── vars/
│   ├── cache_services/
│   │   ├── defaults/
│   │   ├── handlers/
│   │   ├── tasks/
│   │   └── templates/
│   └── fastapi_app/
│       ├── defaults/
│       ├── handlers/
│       ├── tasks/
│       └── templates/
├── playbooks/
│   ├── site.yml
│   ├── nginx.yml
│   ├── cache.yml
│   └── fastapi.yml
└── vagrant-provision.yml
```

## Migration Tasks

1. **Infrastructure Setup**:
   - Create Ansible directory structure
   - Set up inventory files for development and production
   - Create base playbooks

2. **Role Creation**:
   - Create nginx_multisite role with tasks for installation, configuration, and security
   - Create cache_services role for Memcached and Redis
   - Create fastapi_app role for application deployment

3. **Template Migration**:
   - Convert Chef ERB templates to Ansible Jinja2 templates
   - Migrate static files to Ansible role files

4. **Variable Management**:
   - Create defaults and vars files for each role
   - Move Chef node attributes to Ansible variables
   - Secure sensitive information with Ansible Vault

5. **Testing**:
   - Update Vagrantfile to use Ansible provisioner
   - Create test playbooks for each role
   - Verify functionality matches original Chef implementation

6. **Documentation**:
   - Create README files for each role
   - Document variable usage and customization options
   - Provide examples for common deployment scenarios