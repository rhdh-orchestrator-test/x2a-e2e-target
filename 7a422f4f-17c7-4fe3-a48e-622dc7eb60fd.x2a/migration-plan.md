# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The repository has well-structured Chef cookbooks with clear dependencies
- Security configurations are present and need careful migration
- External cookbook dependencies need to be replaced with Ansible Galaxy roles or custom implementations

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, UFW firewall), sysctl security settings

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, dependency on external cookbooks

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies including external cookbooks from Chef Supermarket (nginx, memcached, redisio)
- `solo.json`: Contains the Chef run list and node attributes including Nginx site configurations and security settings
- `solo.rb`: Chef Solo configuration file defining cookbook paths and log settings
- `Vagrantfile`: Defines a Vagrant VM (Fedora 42) for development and testing with port forwarding and networking
- `vagrant-provision.sh`: Shell script to provision the Vagrant VM with Chef and run the cookbooks

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` role from Galaxy or custom implementation
- **memcached (~> 6.0)**: Replace with Ansible's `geerlingguy.memcached` role or custom implementation
- **redisio (~> 7.2.4)**: Replace with Ansible's `geerlingguy.redis` role or custom implementation

### Security Considerations

- **Firewall Configuration**: The Chef cookbook configures UFW firewall rules that need to be migrated to Ansible's `ufw` module
- **fail2ban Configuration**: fail2ban setup needs to be migrated using Ansible's package and template modules
- **SSH Hardening**: SSH security settings (disabling root login, password authentication) need to be migrated
- **SSL Certificate Management**: Self-signed certificate generation needs to be migrated to Ansible
- **Vault/secrets management**:
  - Redis password in cache cookbook: 1 hardcoded password in attributes
  - PostgreSQL credentials in fastapi-tutorial cookbook: 2 hardcoded passwords in recipe
  - Environment variables in .env file: Contains database connection string with credentials
  - SSL certificates: Generated dynamically but need secure handling

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of multiple Nginx site configurations based on node attributes needs careful translation to Ansible variables and templates
- **SSL Certificate Generation**: The self-signed certificate generation logic needs to be replicated in Ansible
- **Security Hardening**: The comprehensive security settings (sysctl, fail2ban, UFW) need careful migration to maintain security posture
- **Service Dependencies**: Ensuring proper service dependencies and ordering in Ansible (e.g., PostgreSQL before FastAPI application)

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Contains security configurations that should be established first

2. **cache** (Priority 2)
   - Moderate complexity with external dependencies
   - Required by the application but can be migrated independently

3. **fastapi-tutorial** (Priority 3)
   - Depends on properly configured Nginx for serving
   - Most complex with database setup, application deployment, and service configuration

### Assumptions

1. The target environment will continue to be Fedora-based systems (specifically Fedora 42 as indicated in the Vagrantfile)
2. The same directory structure for web content and application code will be maintained
3. Self-signed certificates are acceptable for the migrated environment (production would likely require proper certificates)
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The security requirements (fail2ban, UFW, SSH hardening) will remain the same
6. Redis and Memcached configurations will maintain the same memory allocations and settings
7. PostgreSQL database name, user, and credentials can remain the same
8. The Vagrant development environment will be replaced with an equivalent Ansible-based setup

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
├── Vagrantfile
└── README.md
```

## Next Steps

1. Create a detailed inventory of all configuration files, templates, and attributes
2. Develop Ansible roles that replicate the functionality of each Chef cookbook
3. Create a Vagrant environment for testing the Ansible playbooks
4. Implement secure credential management using Ansible Vault
5. Develop comprehensive tests to validate the migrated infrastructure
6. Create documentation for the new Ansible-based deployment process