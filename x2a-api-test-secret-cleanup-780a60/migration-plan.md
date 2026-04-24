# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup with three primary cookbooks: nginx-multisite, cache, and fastapi-tutorial. The migration to Ansible will involve converting these cookbooks to Ansible roles and playbooks while maintaining the same functionality and security practices.

**Scope**: 3 Chef cookbooks with dependencies on external cookbooks
**Complexity**: Medium (standard web server, caching, and application deployment patterns)
**Timeline Estimate**: 2-3 weeks for complete migration

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and proper SSL configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, fail2ban integration, UFW firewall configuration

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration, log directory management

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Manages cookbook dependencies - will be replaced by Ansible Galaxy requirements.yml
- `solo.json`: Contains node attributes and run list - will be replaced by Ansible inventory variables
- `solo.rb`: Chef configuration file - will be replaced by Ansible configuration
- `Vagrantfile`: Defines development VM - can be adapted for Ansible testing
- `vagrant-provision.sh`: Provisions the Vagrant VM with Chef - will be replaced with Ansible provisioning

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be designed for on-premises or local development

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or direct package installation
- **memcached (~> 6.0)**: Replace with Ansible memcached role or direct package installation
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or direct package installation

### Security Considerations

- **SSL Certificate Management**: The current implementation generates self-signed certificates. Migration should maintain this capability or integrate with Let's Encrypt.
- **Security Headers**: Nginx is configured with security headers (HSTS, CSP, X-Frame-Options) that must be preserved.
- **Firewall Configuration**: UFW rules are configured for SSH, HTTP, and HTTPS access.
- **fail2ban Integration**: Configured to protect against brute force attacks.
- **SSH Hardening**: Root login disabled and password authentication disabled.
- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook
  - PostgreSQL credentials are hardcoded in the fastapi-tutorial cookbook
  - These should be migrated to Ansible Vault

### Technical Challenges

- **Multi-site Configuration**: The nginx-multisite cookbook dynamically creates virtual hosts based on node attributes. This pattern needs to be replicated in Ansible using loops or with_items.
- **SSL Certificate Generation**: Self-signed certificate generation logic needs to be preserved or enhanced.
- **Service Dependencies**: The FastAPI application depends on PostgreSQL, which must be started first. This dependency needs to be maintained in Ansible.
- **Configuration File Templating**: Multiple configuration templates need to be converted from ERB to Jinja2 format.

### Migration Order

1. **nginx-multisite** (Priority 1): Core infrastructure component that other services depend on
2. **cache** (Priority 2): Supporting service with external dependencies
3. **fastapi-tutorial** (Priority 3): Application deployment that depends on infrastructure components

### Assumptions

1. The target environment will continue to be Fedora-based systems
2. Self-signed certificates are acceptable for the migrated solution
3. The same security practices should be maintained in the Ansible implementation
4. The FastAPI application source will continue to be pulled from the same Git repository
5. The current network configuration and port mappings should be preserved

## Ansible Structure Recommendation

```
ansible/
├── inventory/
│   ├── group_vars/
│   │   ├── all.yml
│   │   └── web_servers.yml
│   └── hosts.yml
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
├── requirements.yml
└── ansible.cfg
```

## Migration Tasks Breakdown

1. **Infrastructure Setup**
   - Create Ansible directory structure
   - Set up inventory and group variables
   - Create requirements.yml for external role dependencies

2. **nginx-multisite Migration**
   - Convert Nginx configuration templates from ERB to Jinja2
   - Create tasks for installing and configuring Nginx
   - Implement virtual host configuration with loops
   - Implement SSL certificate generation
   - Implement security configurations (fail2ban, UFW)

3. **cache Migration**
   - Create tasks for Memcached installation and configuration
   - Create tasks for Redis installation and configuration
   - Move Redis password to Ansible Vault

4. **fastapi-tutorial Migration**
   - Create tasks for Python and dependencies installation
   - Implement Git repository cloning
   - Create tasks for PostgreSQL setup
   - Move database credentials to Ansible Vault
   - Implement systemd service configuration

5. **Testing and Validation**
   - Update Vagrantfile to use Ansible provisioner
   - Test each role individually
   - Test complete playbook
   - Validate security configurations

6. **Documentation**
   - Document Ansible roles and variables
   - Create usage examples
   - Document Vault usage for secrets management