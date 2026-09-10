# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with 3 cookbooks managing web services, caching infrastructure, and a FastAPI application. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to security configurations, SSL certificate management, and database setup. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication, memcached integration, custom Redis configuration patching, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application with PostgreSQL database backend, including Git deployment and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Python virtual environment setup, Git repository cloning, PostgreSQL database and user creation, systemd service configuration, environment file management

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled virtual hosts, security hardening, and fail2ban protection
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-domain SSL certificates, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security tuning, custom nginx configuration templates

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list and node attributes configuration with site definitions and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support specified in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or cloud-agnostic deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules and custom configuration management

### Security Considerations

- **SSL Certificate Management**: Self-signed certificate generation using OpenSSL commands - migrate to ansible.builtin.openssl_* modules
- **Hardcoded Credentials**: 
  - Redis password: `redis_secure_password_123` in cache cookbook
  - PostgreSQL credentials: `fastapi:fastapi_password` in fastapi-tutorial cookbook
  - Database connection strings in environment files
- **SSH Hardening**: Root login disable and password authentication disable - migrate to ansible.posix.sysctl and lineinfile modules
- **Firewall Configuration**: UFW rules for HTTP/HTTPS/SSH - migrate to community.general.ufw module
- **Fail2ban Configuration**: Custom jail.local template - migrate to ansible.builtin.template module
- **File Permissions**: SSL private keys with group ownership (ssl-cert group) - ensure proper Ansible file module usage

### Technical Challenges

- **Custom Redis Configuration Patching**: The cache cookbook uses a Ruby block to modify Redis config files post-installation - requires conversion to Ansible lineinfile or replace modules with proper regex patterns
- **Multi-site SSL Certificate Generation**: Dynamic certificate creation for multiple domains - needs Ansible loops with openssl_certificate module
- **Service Dependencies**: PostgreSQL must be running before FastAPI application starts - requires proper Ansible handler ordering and service dependencies
- **Template Variable Mapping**: Chef ERB templates need conversion to Jinja2 with attribute mapping from Chef node attributes to Ansible variables
- **Git Repository Management**: FastAPI cookbook clones and syncs Git repositories - migrate to ansible.builtin.git module with proper change detection

### Migration Order

1. **cache** (low risk, standalone service)
   - Simple package installation and service management
   - Self-contained with minimal external dependencies
   - Good starting point for team to establish patterns

2. **nginx-multisite** (moderate complexity)
   - Security configurations can be tested independently
   - SSL certificate generation needs careful validation
   - Templates require Jinja2 conversion

3. **fastapi-tutorial** (high complexity, dependencies)
   - Depends on PostgreSQL being properly configured
   - Application deployment with Git integration
   - Service management and environment configuration
   - Database user and schema creation

### Assumptions

- Target environments will maintain the same OS support (Ubuntu 18.04+, CentOS 7+)
- SSL certificates can remain self-signed for development environments
- PostgreSQL and Redis passwords will be migrated to Ansible Vault for production
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible
- UFW firewall is acceptable for the target environment (vs. iptables or firewalld)
- Systemd is available on target systems for service management
- The nginx sites configuration structure (test.cluster.local, ci.cluster.local, status.cluster.local) will be maintained
- Chef Supermarket cookbooks (nginx, memcached, redisio) functionality can be replicated with Ansible community collections
- Development workflow using Vagrant will be replaced with ansible-playbook execution or molecule testing