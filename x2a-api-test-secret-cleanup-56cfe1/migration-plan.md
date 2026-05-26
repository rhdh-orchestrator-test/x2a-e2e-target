# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Memcached and Redis) and a FastAPI application with PostgreSQL. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:**
- Medium complexity due to multiple services and security configurations
- Moderate number of external dependencies
- Clear separation of concerns in the existing cookbooks

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and fail2ban/ufw configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security headers, firewall configuration

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository deployment, Python virtual environment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks. Lists both local and external cookbook dependencies with version constraints.
- `Vagrantfile`: Defines a Fedora 42 VM for local development with port forwarding and resource allocation.
- `solo.json`: Chef run list and node attributes configuration, including Nginx site definitions and security settings.
- `solo.rb`: Chef Solo configuration specifying cookbook paths and log settings.
- `vagrant-provision.sh`: Bash script to provision the Vagrant VM with Chef, install dependencies, and run Chef Solo.

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be targeting local development or on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or collection (e.g., `ansible.posix.nginx`)
- **memcached (~> 6.0)**: Replace with Ansible memcached role or direct package installation and configuration
- **redisio (~> 7.2.4)**: Replace with Ansible redis role or direct package installation and configuration

### Security Considerations

- **SSL/TLS Configuration**: 
  - Self-signed certificate generation for development
  - Proper certificate paths and permissions
  - Migration approach: Use Ansible's `openssl_*` modules or community.crypto collection

- **Firewall Configuration**:
  - UFW configuration with default deny policy
  - Specific port allowances (SSH, HTTP, HTTPS)
  - Migration approach: Use Ansible's `ufw` module or firewalld equivalent

- **Fail2ban Integration**:
  - Fail2ban jail configuration for SSH and web services
  - Migration approach: Use Ansible to deploy fail2ban configuration files

- **SSH Hardening**:
  - Disable root login
  - Disable password authentication
  - Migration approach: Use Ansible's `lineinfile` module or ssh_config module

- **Vault/secrets management**:
  - Redis password in plaintext in recipe (redis_secure_password_123)
  - PostgreSQL password in plaintext in recipe (fastapi_password)
  - Database connection string in .env file
  - Migration approach: Use Ansible Vault for sensitive data

### Technical Challenges

- **Multi-site Nginx Configuration**: 
  - Description: The current setup dynamically generates Nginx site configurations based on node attributes
  - Mitigation: Use Ansible templates with variable substitution, similar to the current ERB templates

- **SSL Certificate Generation**:
  - Description: Self-signed certificates are generated with specific attributes and permissions
  - Mitigation: Use Ansible's `openssl_certificate` module with proper file permissions

- **Database Initialization**:
  - Description: PostgreSQL database and user creation with specific privileges
  - Mitigation: Use Ansible's `postgresql_*` modules from the community.postgresql collection

- **Service Orchestration**:
  - Description: Proper ordering of service installation, configuration, and startup
  - Mitigation: Use Ansible handlers and proper task dependencies

### Migration Order

1. **nginx-multisite** (Priority 1)
   - Core infrastructure component that other services depend on
   - Includes security hardening that should be applied early

2. **cache** (Priority 2)
   - Supporting services that the application may depend on
   - Relatively self-contained with external dependencies

3. **fastapi-tutorial** (Priority 3)
   - Application deployment that depends on both web server and database
   - More complex with git repository management, virtual environment, and database setup

### Assumptions

1. The target environment will continue to be Fedora-based systems (specifically Fedora 42 as indicated in the Vagrantfile)
2. The same network configuration (ports, IP addresses) will be maintained
3. Self-signed certificates are acceptable for development environments
4. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
5. The current security configurations (fail2ban, ufw, SSH hardening) are appropriate for the target environment
6. Redis and Memcached configurations don't require significant tuning beyond what's currently specified
7. The PostgreSQL database schema is managed by the FastAPI application and doesn't require additional migration steps
8. The current directory structure in /opt and /var will be maintained in the target environment