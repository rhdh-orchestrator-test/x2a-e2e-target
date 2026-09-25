# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing caching services, a FastAPI application, and a multi-site nginx web server with SSL and security hardening. The migration involves converting Chef cookbooks to Ansible playbooks and roles, addressing external dependencies, and maintaining security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including authentication and custom Redis configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication, memcached integration, custom Redis config patching via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment setup, and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python venv creation, PostgreSQL database and user provisioning, systemd service configuration

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled virtual hosts, security hardening, and fail2ban protection
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, self-signed certificate generation, fail2ban integration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbook dependencies (nginx, memcached, redisio)
- `solo.json`: Chef Solo run list and node attributes configuration with site definitions and security settings
- `solo.rb`: Chef Solo configuration file for local cookbook execution
- `Vagrantfile`: Development environment provisioning (requires review for Ansible integration)
- `vagrant-provision.sh`: Shell provisioning script for Vagrant environment setup

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible-community nginx role or custom nginx tasks
- **memcached (~> 6.0)**: Replace with geerlingguy.memcached Ansible role or custom memcached configuration
- **redisio (~> 7.2.4)**: Replace with geerlingguy.redis Ansible role with custom authentication configuration

### Security Considerations

- **Hardcoded Credentials**: Multiple plaintext passwords found requiring Ansible Vault migration:
  - Redis password: `redis_secure_password_123` in cache cookbook
  - PostgreSQL password: `fastapi_password` in fastapi-tutorial cookbook
  - Database connection strings with embedded credentials in .env files
- **SSL Certificate Management**: Self-signed certificate generation needs migration to Ansible crypto modules or Let's Encrypt integration
- **SSH Hardening**: Root login disable and password authentication disable configurations need migration to Ansible ssh hardening tasks
- **Firewall Configuration**: UFW rules and fail2ban jail configurations require migration to Ansible firewall modules
- **System Security**: Sysctl security parameters need migration to Ansible sysctl module

### Technical Challenges

- **Ruby Block Logic**: The cache cookbook contains complex Ruby logic for Redis configuration file manipulation that needs conversion to Ansible lineinfile or template modules
- **Service Dependencies**: PostgreSQL service must be running before database user creation, requiring proper Ansible task ordering and handlers
- **Multi-Site SSL**: Dynamic SSL certificate generation for multiple sites needs conversion to Ansible loops with crypto modules
- **Template Migration**: ERB templates need conversion to Jinja2 format for nginx.conf, security.conf, and fail2ban configurations
- **Git Repository Management**: FastAPI application deployment from Git requires Ansible git module with proper change detection

### Migration Order

1. **cache** (moderate complexity, standalone caching services)
2. **nginx-multisite** (high complexity due to SSL, security, and multi-site configuration)
3. **fastapi-tutorial** (moderate complexity, depends on PostgreSQL and has application-specific requirements)

### Assumptions

- Target environments will maintain Ubuntu/CentOS compatibility as specified in cookbook metadata
- Self-signed certificates are acceptable for development; production may require Let's Encrypt or corporate CA integration
- PostgreSQL will be installed locally rather than using external database services
- Current hardcoded passwords are development placeholders and will be replaced with Ansible Vault encrypted variables
- UFW firewall is the preferred firewall solution (may need adaptation for RHEL/CentOS environments using firewalld)
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and stable
- Vagrant development environment will be maintained or replaced with equivalent Ansible-based local testing
- Current Chef Solo execution model will be replaced with Ansible playbook execution against inventory hosts