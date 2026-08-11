# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure configuration for a multi-site Nginx web server with FastAPI application backend and caching services. The migration to Ansible will involve converting 3 Chef cookbooks with their recipes, templates, and attributes to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- Well-structured Chef cookbooks with clear separation of concerns
- Standard package installations and configurations
- Some security configurations that require careful migration
- Credentials and secrets management needed

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **fastapi-tutorial**:
    - Description: FastAPI Python application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, PostgreSQL database configuration, systemd service management

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: SSL certificate generation, virtual host configuration, security hardening with fail2ban and UFW

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks. Lists both local and external cookbook dependencies.
- `solo.json`: Chef node configuration with run list and attribute overrides. Contains site configurations and security settings.
- `solo.rb`: Chef Solo configuration file specifying cookbook paths and logging settings.
- `Vagrantfile`: Defines development VM using Fedora 42 with port forwarding and resource allocation.
- `vagrant-provision.sh`: Bash script to provision the Vagrant VM with Chef, installs dependencies and runs Chef Solo.

### Target Details

Based on the source configuration files:

- **Operating System**: Fedora 42 (from Vagrantfile) with support for Ubuntu 18.04+ and CentOS 7+ (from cookbook metadata)
- **Virtual Machine Technology**: Libvirt (specified in Vagrantfile)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible `nginx` role or use the `ansible.builtin.package` module to install nginx directly
- **memcached (~> 6.0)**: Replace with Ansible `geerlingguy.memcached` community role or create custom role
- **redisio (~> 7.2.4)**: Replace with Ansible `geerlingguy.redis` community role or create custom role
- **PostgreSQL**: Use Ansible `geerlingguy.postgresql` community role or the `ansible.builtin.postgresql_*` modules

### Security Considerations

- **SSL Certificate Management**: 
  - Self-signed certificates are generated in the Chef cookbook
  - Migration should use Ansible's `openssl_*` modules or `community.crypto` collection
  - Consider integrating with Let's Encrypt for production environments

- **Firewall Configuration**: 
  - UFW firewall rules need to be migrated using Ansible's `community.general.ufw` module
  - Default deny policy with specific allows for SSH, HTTP, and HTTPS

- **Fail2ban Configuration**: 
  - Migrate fail2ban configuration using Ansible's `community.general.fail2ban` module or templates

- **SSH Hardening**:
  - Disable root login and password authentication
  - Use Ansible's `ansible.posix.sshd_config` module for SSH configuration

- **Vault/secrets management**:
  - Redis password (`redis_secure_password_123`) in cache cookbook
  - PostgreSQL database credentials (`fastapi:fastapi_password`) in fastapi-tutorial cookbook
  - Consider using Ansible Vault for storing these secrets

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Challenge: The Chef cookbook dynamically creates multiple virtual hosts based on node attributes
  - Solution: Use Ansible loops with templates to achieve similar functionality

- **Service Orchestration**: 
  - Challenge: Ensuring proper service restart/reload only when needed
  - Solution: Use Ansible handlers and notify mechanism similar to Chef's notifications

- **SSL Certificate Generation**: 
  - Challenge: Self-signed certificate generation logic needs to be preserved
  - Solution: Use Ansible's `openssl_*` modules with conditional checks

- **Database Initialization**: 
  - Challenge: PostgreSQL database and user creation with proper idempotence
  - Solution: Use Ansible's postgresql_* modules with proper when conditions

### Migration Order

1. **cache** (Priority 1 - Low complexity)
   - Simple package installations and configurations
   - Good starting point to establish patterns

2. **nginx-multisite** (Priority 2 - Medium complexity)
   - Core infrastructure component
   - Multiple templates and configurations
   - Security hardening components

3. **fastapi-tutorial** (Priority 3 - Medium complexity)
   - Application deployment with database dependencies
   - Requires the web server to be configured first

### Assumptions

1. The target environment will continue to use the same operating systems (Fedora/Ubuntu/CentOS)
2. Self-signed certificates are acceptable for development, but production may require proper CA-signed certificates
3. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
4. The same security policies (disable root SSH, password authentication, etc.) will be maintained
5. The same virtual host configurations will be needed in the new environment
6. Vagrant will continue to be used for development/testing environments

## Ansible Structure Recommendation

```
ansible-project/
├── inventories/
│   ├── development/
│   │   ├── hosts.yml
│   │   └── group_vars/
│   └── production/
│       ├── hosts.yml
│       └── group_vars/
├── roles/
│   ├── nginx_multisite/
│   │   ├── defaults/main.yml  # Former node attributes
│   │   ├── tasks/main.yml     # Main tasks (former default.rb)
│   │   ├── tasks/security.yml # Security tasks
│   │   ├── tasks/ssl.yml      # SSL certificate tasks
│   │   ├── tasks/sites.yml    # Site configuration tasks
│   │   └── templates/         # Jinja2 templates (former ERB)
│   ├── cache/
│   │   ├── defaults/main.yml
│   │   ├── tasks/main.yml
│   │   ├── tasks/redis.yml
│   │   └── tasks/memcached.yml
│   └── fastapi_app/
│       ├── defaults/main.yml
│       ├── tasks/main.yml
│       ├── tasks/postgresql.yml
│       └── templates/
├── playbooks/
│   ├── site.yml              # Main playbook
│   ├── nginx.yml             # Nginx-specific playbook
│   ├── cache.yml             # Cache-specific playbook
│   └── fastapi.yml           # FastAPI-specific playbook
├── group_vars/
│   └── all/
│       ├── main.yml          # Common variables
│       └── vault.yml         # Encrypted secrets
└── vagrant/
    └── Vagrantfile           # For development testing
```

## Next Steps

1. Create Ansible inventory structure for development and production environments
2. Convert Chef attributes to Ansible variables in group_vars and role defaults
3. Create Ansible roles for each Chef cookbook, starting with the cache role
4. Migrate templates from ERB to Jinja2 format
5. Create Ansible Vault for secrets management
6. Develop testing strategy using Molecule or similar tools
7. Create documentation for the new Ansible structure