# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies, configuration templates, and security settings.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 2-3 weeks
- Testing and Validation: 1 week
- Documentation and Knowledge Transfer: 1 week
- **Total**: 5-6 weeks

**Complexity Assessment**: Medium
- Well-structured Chef cookbooks with clear separation of concerns
- Standard infrastructure components (Nginx, Redis, Memcached, PostgreSQL)
- Security configurations that need careful migration
- Credentials that need to be migrated to Ansible Vault

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site-specific configurations
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

- `Berksfile`: Dependency management file listing both local cookbooks and external dependencies from Chef Supermarket
- `solo.json`: Chef Solo configuration file containing the run list and node attributes
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and log settings
- `Vagrantfile`: Defines the development VM using Fedora 42, with port forwarding and resource allocation
- `vagrant-provision.sh`: Bash script to provision the Vagrant VM with Chef Solo

### Target Details

- **Operating System**: Fedora (based on Vagrantfile specifying "generic/fedora42"), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Libvirt (specified in Vagrantfile)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role (e.g., geerlingguy.nginx)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible redis role (e.g., geerlingguy.redis)

### Security Considerations

- **SSL Certificate Management**: 
  - Current implementation generates self-signed certificates
  - Migration approach: Use Ansible's openssl_* modules for certificate generation or integrate with ansible-role-certbot for Let's Encrypt

- **Firewall Configuration (UFW)**:
  - Current implementation configures UFW with specific rules
  - Migration approach: Use Ansible's ufw module to configure identical rules

- **Fail2Ban Configuration**:
  - Current implementation installs and configures fail2ban
  - Migration approach: Create an Ansible role for fail2ban configuration

- **SSH Hardening**:
  - Current implementation disables root login and password authentication
  - Migration approach: Use Ansible's lineinfile module or dedicated ssh hardening role

- **Vault/secrets management**:
  - Redis password in cache cookbook: "redis_secure_password_123"
  - PostgreSQL credentials in fastapi-tutorial cookbook: "fastapi:fastapi_password"
  - Environment variables in .env file for FastAPI application
  - Migration approach: Store all credentials in Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Challenge: Maintaining the dynamic generation of site configurations
  - Mitigation: Use Ansible's template module with loops to generate site configurations from variables

- **SSL Certificate Management**: 
  - Challenge: Ensuring secure certificate generation and management
  - Mitigation: Use Ansible's crypto modules or integrate with certbot for Let's Encrypt

- **Service Dependencies**: 
  - Challenge: Ensuring proper service startup order (e.g., PostgreSQL before FastAPI)
  - Mitigation: Use Ansible's meta dependencies and handlers to manage service ordering

- **Redis Configuration Hack**: 
  - Challenge: The Chef cookbook contains a hack to fix Redis configuration
  - Mitigation: Create a proper Redis configuration template in Ansible that doesn't require post-processing

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Contains security configurations that should be established first

2. **cache** (Priority 2)
   - Supports the application layer
   - Moderate complexity with Redis authentication

3. **fastapi-tutorial** (Priority 3)
   - Application layer that depends on both nginx and cache components
   - Involves database setup, application deployment, and service configuration

### Assumptions

1. The target environment will continue to be Fedora-based, with support for Ubuntu and CentOS as specified in the cookbook metadata
2. Self-signed certificates are acceptable for the migrated solution (production environments may require proper CA-signed certificates)
3. The current security configurations (fail2ban, ufw, SSH hardening) are appropriate for the target environment
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current Redis and PostgreSQL passwords are development passwords and will be replaced with proper secure passwords in production
6. The Vagrant development environment will be maintained for testing the Ansible playbooks

## Ansible Structure Recommendation

```
ansible-nginx-multisite/
├── inventories/
│   ├── development/
│   │   ├── group_vars/
│   │   │   └── all/
│   │   │       ├── vars.yml
│   │   │       └── vault.yml
│   │   └── hosts.yml
│   └── production/
│       ├── group_vars/
│       │   └── all/
│       │       ├── vars.yml
│       │       └── vault.yml
│       └── hosts.yml
├── roles/
│   ├── nginx-multisite/
│   │   ├── defaults/
│   │   ├── files/
│   │   ├── handlers/
│   │   ├── tasks/
│   │   ├── templates/
│   │   └── vars/
│   ├── cache/
│   │   ├── defaults/
│   │   ├── handlers/
│   │   ├── tasks/
│   │   ├── templates/
│   │   └── vars/
│   └── fastapi-tutorial/
│       ├── defaults/
│       ├── handlers/
│       ├── tasks/
│       ├── templates/
│       └── vars/
├── site.yml
├── nginx.yml
├── cache.yml
├── fastapi.yml
└── vagrant-playbook.yml
```

## Testing Strategy

1. Create a Vagrant environment similar to the current one but using Ansible provisioning
2. Develop and test each role individually
3. Test the complete playbook to ensure all components work together
4. Verify security configurations using automated scanning tools
5. Perform manual testing of the web applications and caching services

## Knowledge Transfer Plan

1. Document each Ansible role with README files explaining purpose and configuration options
2. Create a migration report comparing Chef and Ansible implementations
3. Conduct a walkthrough session with the team to explain the migration approach
4. Provide examples of common tasks (adding new sites, updating SSL certificates, etc.)