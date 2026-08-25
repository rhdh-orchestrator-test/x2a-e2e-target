# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx setup with caching services and a FastAPI application. The migration to Ansible will involve converting 3 Chef cookbooks with their recipes, templates, and attributes to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The codebase is well-structured with clear separation of concerns
- No custom resources or complex Chef-specific patterns are used
- Standard package installation and configuration patterns are used throughout

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw, sysctl)

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies (both local and external from Chef Supermarket)
  - Migration consideration: Replace with Ansible Galaxy requirements.yml
  
- `solo.json`: Contains the run list and node attributes for Chef Solo
  - Migration consideration: Convert to Ansible group_vars or host_vars

- `solo.rb`: Chef Solo configuration file
  - Migration consideration: Replace with ansible.cfg

- `Vagrantfile`: Defines the development VM configuration
  - Migration consideration: Update to use Ansible provisioner instead of Chef

- `vagrant-provision.sh`: Shell script to install Chef and run Chef Solo
  - Migration consideration: Replace with Ansible provisioning commands

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (from Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (from cookbook metadata)
- **Virtual Machine Technology**: Vagrant with libvirt provider
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or direct package installation
- **memcached (~> 6.0)**: Replace with Ansible memcached role or direct package installation
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or direct package installation

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated for each site
  - Migration approach: Use Ansible's openssl_* modules or community.crypto collection

- **Firewall Configuration**: 
  - UFW is configured to allow only SSH, HTTP, and HTTPS
  - Migration approach: Use Ansible's ufw module

- **SSH Hardening**: 
  - Root login disabled
  - Password authentication disabled
  - Migration approach: Use Ansible's lineinfile or template module for sshd_config

- **System Hardening**: 
  - Sysctl security settings
  - Migration approach: Use Ansible's sysctl module

- **Fail2ban Configuration**: 
  - Custom jail configuration
  - Migration approach: Use Ansible's template module or community.general.fail2ban module

- **Vault/secrets management**:
  - Redis password is hardcoded in the cache cookbook
  - PostgreSQL password is hardcoded in the fastapi-tutorial cookbook
  - Migration approach: Use Ansible Vault for sensitive data

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Challenge: Maintaining the dynamic generation of site configurations
  - Mitigation: Use Ansible's with_items/loop constructs with templates

- **SSL Certificate Generation**: 
  - Challenge: Ensuring idempotent certificate generation
  - Mitigation: Use Ansible's openssl_* modules with proper changed_when conditions

- **Service Dependencies**: 
  - Challenge: Ensuring proper ordering of service installations and configurations
  - Mitigation: Use Ansible's meta dependencies between roles and handlers for notifications

- **Database Initialization**: 
  - Challenge: Idempotent database and user creation
  - Mitigation: Use Ansible's postgresql_* modules with proper when conditions

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Contains security configurations that should be applied first

2. **cache** (Priority 2)
   - Supporting services that the application may depend on
   - Moderate complexity with external dependencies

3. **fastapi-tutorial** (Priority 3)
   - Application deployment that depends on infrastructure being in place
   - Involves database setup and application configuration

### Assumptions

1. The target environment will continue to be Fedora 42 or compatible Linux distributions
2. The same network configuration (ports, IPs) will be maintained
3. Self-signed certificates are acceptable for the migrated solution
4. The FastAPI application source code will remain the same
5. The PostgreSQL database schema does not need migration, only the database server configuration
6. No CI/CD pipeline integration is required as part of this migration
7. The Vagrant development environment should be preserved with equivalent functionality

## Ansible Structure Recommendation

```
ansible-nginx-multisite/
├── ansible.cfg
├── inventory/
│   ├── hosts
│   ├── group_vars/
│   │   └── all.yml
│   └── host_vars/
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
├── requirements.yml
└── Vagrantfile
```

## Testing Strategy

1. Develop and test each role individually using Molecule
2. Create integration tests to verify interactions between roles
3. Test the complete playbook against a Vagrant VM matching the production environment
4. Verify all functionality against the original Chef implementation using automated tests

## Knowledge Transfer Plan

1. Document each Ansible role with README files explaining purpose and configuration options
2. Create a migration report comparing the original Chef implementation with the new Ansible implementation
3. Conduct a walkthrough session with the operations team
4. Provide examples of common maintenance tasks in the new Ansible structure