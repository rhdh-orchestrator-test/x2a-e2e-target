# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing caching services, a FastAPI application, and a multi-site nginx web server with SSL termination. The migration involves converting Chef cookbooks to Ansible playbooks and roles, addressing external dependencies, and maintaining security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including authentication, logging, and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis password authentication, custom log directory creation, configuration file patching via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python venv creation, PostgreSQL database and user provisioning, systemd service management

**nginx-multisite**:
- Description: Nginx reverse proxy with SSL-enabled multi-site hosting, security hardening, and self-signed certificate generation
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multiple SSL virtual hosts, fail2ban integration, UFW firewall configuration, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbook dependencies (nginx, memcached, redisio)
- `solo.json`: Chef Solo run list and node attributes configuration for all three cookbooks
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning (likely for testing)
- `vagrant-provision.sh`: Shell script for Vagrant VM setup

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in metadata.rb files)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or cloud-agnostic deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks

### Security Considerations

- **Hardcoded Credentials**: Multiple plaintext passwords found requiring Ansible Vault migration:
  - Redis password: `redis_secure_password_123` in cache cookbook
  - PostgreSQL password: `fastapi_password` in fastapi-tutorial cookbook
  - Database connection strings with embedded credentials in .env files
- **SSL Certificate Management**: Self-signed certificate generation needs migration to ansible.builtin.openssl_* modules
- **SSH Hardening**: Root login disable and password authentication disable configurations
- **Firewall Configuration**: UFW rules for HTTP/HTTPS/SSH ports
- **Fail2ban Integration**: Jail configuration templates for intrusion prevention
- **Sysctl Security Tuning**: Kernel parameter hardening via template

### Technical Challenges

- **Ruby Block Logic**: The cache cookbook contains complex Ruby code for Redis configuration file manipulation that needs conversion to Ansible lineinfile or template modules
- **Multi-Site SSL Configuration**: Dynamic SSL certificate generation and nginx virtual host creation based on node attributes requires Ansible loops and conditionals
- **Service Dependencies**: PostgreSQL must be running before FastAPI application deployment, requiring proper task ordering and handlers
- **File Permissions**: Complex SSL certificate permissions (ssl-cert group) need careful mapping to Ansible file module
- **Git Repository Management**: FastAPI cookbook clones and syncs git repositories requiring ansible.builtin.git module configuration

### Migration Order

1. **cache** (moderate complexity, standalone service)
2. **nginx-multisite** (high complexity due to SSL and security features, but no external service dependencies)
3. **fastapi-tutorial** (highest complexity due to database dependencies and application deployment)

### Assumptions

- Chef Supermarket cookbooks (nginx, memcached, redisio) functionality will be replaced with native Ansible modules
- Self-signed certificates are acceptable for the target environment (production may require CA-signed certificates)
- PostgreSQL installation and configuration is handled by the fastapi-tutorial cookbook (no separate database cookbook dependency)
- The target environment supports systemd for service management
- UFW is the preferred firewall solution (iptables may be needed for RHEL/CentOS environments)
- Development and production environments use the same SSL certificate approach
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible during migration
- Chef Solo configuration can be directly translated to Ansible inventory and group_vars without significant restructuring