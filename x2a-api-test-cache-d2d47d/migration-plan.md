# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with 3 cookbooks managing caching services, a FastAPI application, and a multi-site nginx reverse proxy with SSL termination. The migration involves converting Chef cookbooks to Ansible playbooks and roles, addressing external cookbook dependencies, and migrating security configurations including firewall rules, fail2ban, and SSL certificate management.

**Estimated Timeline**: 3-4 weeks for complete migration
**Complexity**: Medium - straightforward service configurations with some security hardening
**Team Coordination**: Requires coordination between application, infrastructure, and security teams

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached service, Redis with password authentication (redis_secure_password_123), custom Redis configuration patching, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service management, environment configuration file

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening, and fail2ban integration
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, self-signed certificate generation, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef cookbook dependency management - defines external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo configuration with run list and node attributes - contains site configurations and security settings
- `solo.rb`: Chef Solo execution configuration
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be VM-based deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx configuration
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with ansible.builtin.package, custom Redis configuration templates, and service management

### Security Considerations

- **Hardcoded Credentials**: Redis password (redis_secure_password_123) and PostgreSQL credentials (fastapi:fastapi_password) are hardcoded in recipes - migrate to Ansible Vault
- **SSL Certificate Management**: Self-signed certificate generation for development environments - consider using ansible.builtin.openssl_* modules
- **SSH Hardening**: Root login disabled, password authentication disabled - migrate to ansible.posix.sshd_config module
- **Firewall Configuration**: UFW rules for SSH, HTTP, HTTPS - migrate to community.general.ufw module
- **Fail2ban Configuration**: Custom jail configuration - migrate using ansible.builtin.template
- **Sysctl Security Tuning**: Custom security parameters - migrate to ansible.posix.sysctl module
- **Credential Types per Module**:
  - cache: Redis authentication password
  - fastapi-tutorial: PostgreSQL database credentials, application environment variables
  - nginx-multisite: SSL certificate generation (self-signed for development)

### Technical Challenges

- **Redis Configuration Patching**: The cache cookbook includes a Ruby block that manually edits Redis configuration files to remove specific directives - this will need to be replaced with proper Jinja2 templating in Ansible
- **Multi-site SSL Management**: Dynamic SSL certificate generation for multiple sites requires careful loop handling in Ansible playbooks
- **Service Dependencies**: PostgreSQL must be running before FastAPI application starts - requires proper task ordering and handlers in Ansible
- **File Permissions**: SSL private keys have specific group ownership (ssl-cert) that must be maintained during migration

### Migration Order

1. **cache** (low risk, standalone service) - Start with caching services as they have minimal dependencies
2. **nginx-multisite** (moderate complexity) - Migrate web server and security configurations second
3. **fastapi-tutorial** (high complexity, database dependencies) - Migrate application last due to database and service dependencies

### Assumptions

- Development environment uses self-signed certificates (production SSL certificate management strategy not defined)
- PostgreSQL installation and configuration is handled by system packages (no custom PostgreSQL tuning visible)
- All services run on single nodes (no clustering or high availability configuration present)
- UFW is the preferred firewall solution (no iptables rules defined)
- Redis configuration patching suggests the redisio cookbook may have compatibility issues that required workarounds
- Site document root paths differ between attributes/default.rb (/opt/server/*) and solo.json (/var/www/*) - clarification needed on correct paths
- FastAPI application runs as root user (security consideration for production deployment)
- No backup or monitoring configurations are present in the current setup
- Git repository access for FastAPI tutorial assumes public repository (no authentication configured)