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
    - Description: Configures nginx with multiple SSL-enabled subdomains, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw, sysctl)

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

- **cache**:
    - Description: Configures caching services (memcached and redis) with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks - will be replaced by Ansible requirements.yml
- `solo.json`: Chef configuration data - will be converted to Ansible group_vars or host_vars
- `solo.rb`: Chef configuration file - will be replaced by ansible.cfg
- `Vagrantfile`: Development environment configuration - can be adapted for Ansible testing
- `vagrant-provision.sh`: Provisioning script - will be replaced by Ansible playbook calls

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be designed for on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or direct package installation
- **memcached (~> 6.0)**: Replace with Ansible memcached role or direct package installation
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or direct package installation

### Security Considerations

- **SSL Certificate Management**: The current implementation generates self-signed certificates. Migration should maintain this capability while allowing for future integration with Let's Encrypt or other certificate providers.
- **Firewall Configuration**: UFW rules need to be migrated to equivalent Ansible UFW module tasks.
- **Fail2ban Configuration**: Configuration needs to be migrated to Ansible tasks.
- **SSH Hardening**: SSH security configurations need to be migrated to Ansible tasks.
- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook (`redis_secure_password_123`)
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook (`fastapi:fastapi_password`)
  - No external vault integration is currently used

### Technical Challenges

- **Multi-site Configuration**: The nginx-multisite cookbook dynamically creates site configurations based on attributes. This pattern needs to be replicated in Ansible using templates and variables.
- **Service Dependencies**: The FastAPI application depends on PostgreSQL, and the nginx configuration depends on the SSL certificates. These dependencies need to be maintained in the Ansible playbook ordering.
- **SSL Certificate Generation**: The self-signed certificate generation logic needs to be replicated in Ansible.
- **Security Hardening**: The comprehensive security configurations (sysctl, SSH, fail2ban, UFW) need to be carefully migrated to maintain the same security posture.

### Migration Order

1. **cache** (Priority 1): Lowest complexity, minimal dependencies
2. **nginx-multisite** (Priority 2): Medium complexity, no external dependencies but has multiple components
3. **fastapi-tutorial** (Priority 3): Highest complexity due to application deployment and database configuration

### Assumptions

1. The target environment will continue to be Fedora-based systems
2. Self-signed certificates are acceptable for the migrated solution
3. The same security hardening measures are required in the Ansible implementation
4. The FastAPI application source will continue to be pulled from the same Git repository
5. No changes to the application architecture are planned as part of this migration

## Ansible Structure Recommendation

```
ansible-nginx-fastapi/
├── ansible.cfg
├── inventory/
│   ├── hosts
│   ├── group_vars/
│   │   └── all.yml
│   └── host_vars/
├── roles/
│   ├── nginx-multisite/
│   │   ├── defaults/
│   │   ├── files/
│   │   ├── handlers/
│   │   ├── tasks/
│   │   ├── templates/
│   │   └── vars/
│   ├── fastapi-tutorial/
│   │   ├── defaults/
│   │   ├── files/
│   │   ├── handlers/
│   │   ├── tasks/
│   │   ├── templates/
│   │   └── vars/
│   └── cache/
│       ├── defaults/
│       ├── handlers/
│       ├── tasks/
│       ├── templates/
│       └── vars/
├── playbooks/
│   ├── site.yml
│   ├── nginx.yml
│   ├── fastapi.yml
│   └── cache.yml
└── Vagrantfile
```

## Migration Tasks

1. **Setup Ansible Project Structure**
   - Create directory structure
   - Configure ansible.cfg
   - Create inventory files

2. **Migrate Common Variables**
   - Convert solo.json and attributes to group_vars/all.yml
   - Define role-specific variables in role defaults

3. **Migrate Cache Role**
   - Create tasks for memcached installation and configuration
   - Create tasks for Redis installation with password authentication
   - Create handlers for service restarts

4. **Migrate Nginx Role**
   - Create tasks for Nginx installation
   - Create templates for site configurations
   - Create tasks for SSL certificate generation
   - Create tasks for security configurations

5. **Migrate FastAPI Role**
   - Create tasks for Python and dependencies installation
   - Create tasks for application deployment
   - Create tasks for PostgreSQL configuration
   - Create templates for service files and environment configuration

6. **Create Playbooks**
   - Create main site.yml playbook
   - Create role-specific playbooks for individual component testing

7. **Update Vagrant Configuration**
   - Modify Vagrantfile to use Ansible provisioner
   - Remove vagrant-provision.sh

8. **Testing**
   - Test each role individually
   - Test complete deployment
   - Verify security configurations

9. **Documentation**
   - Update README with Ansible usage instructions
   - Document variables and customization options