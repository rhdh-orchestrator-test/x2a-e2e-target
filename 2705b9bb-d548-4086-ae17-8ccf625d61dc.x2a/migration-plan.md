# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup with three cookbooks: `nginx-multisite`, `cache`, and `fastapi-tutorial`. The migration to Ansible will involve converting these cookbooks to Ansible roles and playbooks. The complexity is moderate, with an estimated timeline of 2-3 weeks for a complete migration, including testing and documentation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures nginx with multiple SSL-enabled subdomains, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, fail2ban integration, UFW firewall setup, security hardening

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Configures FastAPI tutorial application with PostgreSQL database
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, PostgreSQL database configuration, systemd service management, Git repository deployment

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies (both local and external). Will be replaced by Ansible Galaxy requirements.yml.
- `solo.json`: Contains node attributes and run list. Will be replaced by Ansible inventory variables.
- `solo.rb`: Chef Solo configuration. Will be replaced by Ansible configuration.
- `Vagrantfile`: Defines the development VM. Can be adapted for Ansible testing with minimal changes.
- `vagrant-provision.sh`: Provisioning script for Vagrant. Will be replaced by Ansible playbook calls.

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or manual package installation
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role or manual Redis installation and configuration

### Security Considerations

- **SSL Certificate Management**: The current setup generates self-signed certificates. Migration should maintain this capability using Ansible's openssl_* modules.
- **Firewall Configuration**: UFW rules need to be migrated to Ansible's ufw module.
- **fail2ban Integration**: Configuration needs to be migrated to Ansible templates.
- **SSH Hardening**: SSH configuration hardening needs to be migrated to Ansible templates.
- **Vault/secrets management**:
  - Redis password in cache cookbook: "redis_secure_password_123"
  - PostgreSQL credentials in fastapi-tutorial cookbook: User "fastapi" with password "fastapi_password"
  - These should be migrated to Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of multiple site configurations based on attributes will need careful translation to Ansible variables and templates.
- **Service Dependencies**: Ensuring proper ordering of service installations and configurations, particularly for the FastAPI application which depends on PostgreSQL.
- **SSL Certificate Generation**: Ensuring the self-signed certificate generation works correctly in Ansible.
- **System Hardening**: Ensuring all security configurations are properly translated to Ansible equivalents.

### Migration Order

1. **cache** (low complexity): Simple Redis and Memcached configuration with minimal dependencies.
2. **nginx-multisite** (moderate complexity): Core infrastructure component with security configurations.
3. **fastapi-tutorial** (moderate complexity): Application deployment with database dependencies.

### Assumptions

1. The target environment will continue to be Fedora/Ubuntu/CentOS based systems.
2. Self-signed certificates are acceptable for development/testing (production would likely use Let's Encrypt or other CA).
3. The current security configurations are appropriate for the target environment.
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available.
5. The current Redis and Memcached configurations meet performance requirements.
6. The current PostgreSQL configuration is sufficient for the FastAPI application.

## Ansible Structure Recommendation

```
ansible-project/
├── inventories/
│   ├── development/
│   │   ├── group_vars/
│   │   │   └── all.yml  # Variables from solo.json
│   │   └── hosts        # Development hosts
│   └── production/
│       ├── group_vars/
│       │   └── all.yml  # Production variables
│       └── hosts        # Production hosts
├── roles/
│   ├── nginx-multisite/
│   │   ├── defaults/
│   │   │   └── main.yml  # From attributes/default.rb
│   │   ├── tasks/
│   │   │   ├── main.yml  # From recipes/default.rb
│   │   │   ├── nginx.yml  # From recipes/nginx.rb
│   │   │   ├── security.yml  # From recipes/security.rb
│   │   │   ├── ssl.yml  # From recipes/ssl.rb
│   │   │   └── sites.yml  # From recipes/sites.rb
│   │   └── templates/
│   │       ├── nginx.conf.j2  # From templates/default/nginx.conf.erb
│   │       ├── security.conf.j2  # From templates/default/security.conf.erb
│   │       ├── site.conf.j2  # From templates/default/site.conf.erb
│   │       ├── fail2ban.jail.local.j2  # From templates/default/fail2ban.jail.local.erb
│   │       └── sysctl-security.conf.j2  # From templates/default/sysctl-security.conf.erb
│   ├── cache/
│   │   ├── defaults/
│   │   │   └── main.yml  # Redis and Memcached configuration
│   │   └── tasks/
│   │       └── main.yml  # From recipes/default.rb
│   └── fastapi-tutorial/
│       ├── defaults/
│       │   └── main.yml  # Application configuration
│       ├── tasks/
│       │   └── main.yml  # From recipes/default.rb
│       └── templates/
│           └── fastapi-tutorial.service.j2  # Systemd service template
├── playbooks/
│   ├── site.yml  # Main playbook (equivalent to run_list)
│   ├── nginx.yml  # Nginx-specific playbook
│   ├── cache.yml  # Cache-specific playbook
│   └── fastapi.yml  # FastAPI-specific playbook
├── requirements.yml  # Ansible Galaxy requirements (from Berksfile)
└── Vagrantfile  # Updated for Ansible provisioning
```

## Testing Strategy

1. Create a parallel Ansible structure while keeping the Chef code intact
2. Update the Vagrantfile to use Ansible provisioning instead of Chef
3. Test each role individually using Molecule or simple Vagrant VMs
4. Perform integration testing with all roles combined
5. Compare the results with the original Chef-provisioned environment

## Timeline Estimate

- **Week 1**: Setup Ansible structure, convert cache cookbook
- **Week 2**: Convert nginx-multisite cookbook, begin testing
- **Week 3**: Convert fastapi-tutorial cookbook, integration testing, documentation