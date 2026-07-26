# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with FastAPI application and caching services. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Scope**: 3 Chef cookbooks with external dependencies
**Complexity**: Medium
**Estimated Timeline**: 2-3 weeks

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw, sysctl)

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

- **cache**:
    - Description: Configures caching services (Memcached and Redis) with security settings
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists both local and external dependencies
- `solo.json`: Chef Solo configuration file with run list and node attributes
- `solo.rb`: Chef Solo configuration file with file paths and log settings
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef
- `Vagrantfile`: Vagrant configuration file for development environment

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be a local development environment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible's `nginx` role or direct package installation and configuration
- **memcached (~> 6.0)**: Replace with Ansible's `geerlingguy.memcached` role or direct package installation
- **redisio (~> 7.2.4)**: Replace with Ansible's `geerlingguy.redis` role or direct package installation and configuration

### Security Considerations

- **Firewall Configuration**: The Chef cookbook configures UFW; migrate to Ansible's `firewalld` or `ufw` modules
- **Fail2ban Setup**: Migrate fail2ban configuration to Ansible tasks
- **SSH Hardening**: Migrate SSH security settings (disable root login, password authentication) to Ansible tasks
- **SSL Certificate Management**: Migrate self-signed certificate generation to Ansible tasks
- **Vault/secrets management**: 
  - Redis password is hardcoded in the cache cookbook
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook
  - Consider using Ansible Vault for these secrets

### Technical Challenges

- **Multi-site Configuration**: The dynamic generation of multiple Nginx sites will need careful translation to Ansible templates and loops
- **SSL Certificate Generation**: Self-signed certificate generation logic needs to be preserved in Ansible
- **Service Dependencies**: Ensuring proper ordering of service installations and configurations (e.g., PostgreSQL before FastAPI application)
- **Idempotency**: Ensuring all operations remain idempotent, especially the database user creation and SSL certificate generation

### Migration Order

1. **nginx-multisite** (Priority 1): Foundation for web services, relatively self-contained
2. **cache** (Priority 2): Independent service with external dependencies
3. **fastapi-tutorial** (Priority 3): Application deployment that may depend on the web server configuration

### Assumptions

1. The target environment will continue to be Fedora-based systems
2. The same directory structure for web content will be maintained
3. Self-signed certificates are acceptable for the migrated solution
4. The FastAPI application source will continue to be pulled from the same Git repository
5. The same security hardening measures will be required in the Ansible implementation
6. The Vagrant development workflow will be preserved, but using Ansible provisioner instead of Chef

## Ansible Structure Recommendation

```
ansible/
├── inventories/
│   └── development/
│       ├── hosts
│       └── group_vars/
│           └── all.yml
├── roles/
│   ├── nginx-multisite/
│   │   ├── defaults/
│   │   ├── tasks/
│   │   ├── templates/
│   │   └── files/
│   ├── fastapi-tutorial/
│   │   ├── defaults/
│   │   ├── tasks/
│   │   └── templates/
│   └── cache/
│       ├── defaults/
│       ├── tasks/
│       └── templates/
├── playbooks/
│   ├── site.yml
│   ├── nginx.yml
│   ├── cache.yml
│   └── fastapi.yml
└── vagrant-ansible.yml
```

## Migration Steps

1. **Setup Ansible Structure**: Create the directory structure for Ansible roles and playbooks
2. **Convert Cookbooks to Roles**: Migrate each cookbook to an equivalent Ansible role
3. **Create Playbooks**: Develop playbooks that orchestrate the roles
4. **Migrate Variables**: Convert Chef attributes to Ansible variables
5. **Implement Templates**: Convert ERB templates to Jinja2 templates
6. **Secure Credentials**: Move hardcoded credentials to Ansible Vault
7. **Test Individual Roles**: Test each role independently
8. **Integration Testing**: Test the complete playbook
9. **Update Vagrant Configuration**: Modify Vagrantfile to use Ansible provisioner
10. **Documentation**: Update documentation to reflect the new Ansible-based workflow