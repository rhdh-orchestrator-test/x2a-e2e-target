# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing caching services, a FastAPI application, and a multi-site nginx web server with SSL and security hardening. The migration involves converting Chef cookbooks to Ansible playbooks and roles, addressing external cookbook dependencies, and migrating security configurations including SSL certificate management and firewall rules.

**Estimated Timeline**: 4-6 weeks for complete migration
**Complexity**: Medium - straightforward service configurations with some security hardening complexity
**Team Coordination**: Requires coordination between web operations, application deployment, and security teams

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis password authentication, custom log directory creation, configuration file patching via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python application deployment with PostgreSQL database, virtual environment setup, and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment, PostgreSQL database and user creation, systemd service configuration

**nginx-multisite**:
- Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening via fail2ban and UFW firewall, and self-signed certificate generation
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site configuration, SSL certificate generation, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security parameters

### Infrastructure Files

- `Berksfile`: Chef cookbook dependency management - defines external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run configuration with run_list and node attributes for site configuration and security settings
- `solo.rb`: Chef Solo configuration file for local cookbook execution
- `Vagrantfile`: Development environment provisioning configuration
- `vagrant-provision.sh`: Shell script for Vagrant VM provisioning

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks

### Security Considerations

- **SSL Certificate Management**: Self-signed certificate generation using OpenSSL commands - migrate to community.crypto.openssl_* modules for certificate generation and management
- **Firewall Configuration**: UFW firewall rules for SSH, HTTP, HTTPS - migrate to community.general.ufw module
- **SSH Hardening**: Root login disable and password authentication disable via sshd_config modifications - migrate to ansible.posix.sshd_config module
- **Fail2ban Configuration**: Custom jail.local template for intrusion prevention - migrate to community.general.fail2ban module
- **Sysctl Security Parameters**: Kernel security parameter tuning via sysctl.d configuration - migrate to ansible.posix.sysctl module
- **Credential Patterns Identified**:
  - Redis authentication password hardcoded in recipe (redis_secure_password_123)
  - PostgreSQL database password hardcoded in recipe (fastapi_password)
  - SSL certificate generation with hardcoded subject information
  - Environment file with database connection string containing credentials

### Technical Challenges

- **Ruby Block Logic**: The cache cookbook uses a ruby_block to perform complex Redis configuration file manipulation - will need to be replaced with ansible.builtin.lineinfile or ansible.builtin.replace modules with multiple tasks
- **Dynamic Site Configuration**: The nginx-multisite cookbook dynamically creates virtual host configurations based on node attributes - will require Jinja2 templating and loop constructs in Ansible
- **Service Dependencies**: PostgreSQL service must be running before database user creation - requires proper task ordering and service state management in Ansible
- **File Permissions and Ownership**: Complex SSL certificate file permissions (ssl-cert group) - requires careful attention to ansible.builtin.file module parameters

### Migration Order

1. **cache** (Priority 1: Low risk, standalone services, clear configuration patterns)
2. **fastapi-tutorial** (Priority 2: Moderate complexity with database dependencies and application deployment)
3. **nginx-multisite** (Priority 3: High complexity with multiple security configurations, SSL management, and dynamic site generation)

### Assumptions

- The target environment will maintain the same OS distribution support (Ubuntu 18.04+, CentOS 7+)
- SSL certificates can remain self-signed for development environments, or will be replaced with proper CA-signed certificates in production
- The Redis password and PostgreSQL credentials will be moved to Ansible Vault for security
- The current Chef Solo execution model will be replaced with standard Ansible playbook execution
- UFW firewall is acceptable for the target environment (vs. iptables or firewalld)
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and compatible
- Systemd is available on target systems for service management
- The nginx configuration templates can be directly converted to Jinja2 format without significant logic changes