# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with caching, security hardening, and SSL-enabled nginx reverse proxy. The migration involves 3 cookbooks with moderate complexity, external dependencies on Chef Supermarket cookbooks, and security configurations that require careful handling of credentials and SSL certificates. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication, memcached integration, custom Redis config patching, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python venv setup, PostgreSQL database and user creation, systemd service management, environment configuration

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening, and fail2ban protection
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, fail2ban integration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management - defines external cookbook dependencies from Chef Supermarket
- `solo.json`: Chef Solo configuration with run list and node attributes for nginx sites and security settings
- `solo.rb`: Chef Solo configuration file for local cookbook execution
- `Vagrantfile`: Development environment provisioning for testing cookbook functionality
- `vagrant-provision.sh`: Shell script for Vagrant VM provisioning and Chef Solo execution

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be VM-based deployment

## Migration Approach

### Key Dependencies to Address

- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis or custom Redis configuration tasks
- **nginx (~> 12.0)**: Replace with nginxinc.nginx_core collection or ansible.builtin.package with custom configuration

### Security Considerations

- **Hardcoded Credentials**: Redis password ('redis_secure_password_123') and PostgreSQL credentials ('fastapi_password') are hardcoded in recipes - migrate to Ansible Vault
- **SSL Certificate Management**: SSL certificate paths defined in attributes (/etc/ssl/certs, /etc/ssl/private) - implement secure certificate deployment with Ansible Vault
- **SSH Hardening**: Root login disabled, password authentication disabled - preserve these security configurations in Ansible
- **Firewall Configuration**: UFW rules for SSH, HTTP, HTTPS - migrate to ansible.posix.ufw module
- **Fail2ban Integration**: Custom jail.local configuration - migrate templates to Ansible Jinja2 templates
- **Sysctl Security Tuning**: Custom kernel parameter hardening - migrate to ansible.posix.sysctl module

### Technical Challenges

- **Redis Configuration Patching**: The cache cookbook includes a Ruby block that manually edits Redis config files to remove specific directives - this will need to be reimplemented using Ansible lineinfile or template modules
- **Multi-Site SSL Configuration**: Complex nginx site configuration with SSL for multiple subdomains requires careful template migration and certificate management
- **Database Initialization**: PostgreSQL database and user creation with proper privilege assignment needs idempotent Ansible implementation
- **Service Dependencies**: Proper service ordering (PostgreSQL before FastAPI, nginx after SSL setup) must be maintained in Ansible playbooks
- **File Permissions and Ownership**: Multiple file/directory ownership changes (www-data, redis user) need proper Ansible user/group management

### Migration Order

1. **cache** (moderate complexity, standalone service)
2. **nginx-multisite** (high complexity due to SSL and security configurations, but foundational)
3. **fastapi-tutorial** (depends on database setup, integrates with nginx proxy)

### Assumptions

- SSL certificates are manually managed and placed in standard locations (/etc/ssl/certs, /etc/ssl/private)
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and stable
- Current Chef Solo execution model will be replaced with Ansible playbook execution
- Development/testing will continue to use Vagrant, but with Ansible provisioner instead of Chef
- Target environments have internet access for package installation and git repository cloning
- PostgreSQL service management and database creation permissions are available on target systems
- UFW firewall is the preferred firewall solution (may need adjustment for RHEL/CentOS environments using firewalld)
- The custom Redis configuration fixes in the Ruby block are still necessary and not resolved by newer Redis versions