# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing caching services, a FastAPI application, and a multi-site nginx reverse proxy with SSL termination. The migration involves converting Chef cookbooks to Ansible playbooks and roles, addressing external cookbook dependencies, and migrating security configurations including fail2ban, UFW firewall, and SSL certificate management.

**Estimated Timeline**: 3-4 weeks for complete migration
**Complexity**: Medium - straightforward service configurations with some security hardening
**Team Coordination**: Single team can handle migration; requires coordination for credential management

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
All module paths confirmed from repository tree analysis.

- **cache**:
    - Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis password authentication (hardcoded), custom Redis configuration patching via ruby_block, memcached integration, log directory management

- **fastapi-tutorial**:
    - Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service management, environment file with database credentials

- **nginx-multisite**:
    - Description: Nginx reverse proxy with multiple SSL-enabled virtual hosts, security hardening via fail2ban and UFW firewall, and self-signed certificate generation
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site SSL configuration, self-signed certificate generation, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef cookbook dependency management - defines external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run configuration with node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file for cookbook paths and node configuration
- `Vagrantfile`: Development environment provisioning (likely contains VM configuration)
- `vagrant-provision.sh`: Shell script for Vagrant provisioning automation

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be local development environment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx configuration
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules for memcached installation and management
- **redisio (~> 7.2.4)**: Replace with ansible.builtin.package, ansible.builtin.template, and ansible.builtin.service modules for Redis configuration and management

### Security Considerations

- **Hardcoded Credentials**: 
  - Redis password 'redis_secure_password_123' in cache cookbook - migrate to Ansible Vault
  - PostgreSQL credentials 'fastapi_password' in fastapi-tutorial cookbook - migrate to Ansible Vault
  - Database URL with embedded credentials in .env file - use Ansible Vault variables
- **SSL Certificate Management**: Self-signed certificate generation via OpenSSL commands - migrate to ansible.builtin.openssl_* modules or community.crypto collection
- **SSH Hardening**: Root login disable and password authentication disable via sed commands - migrate to ansible.builtin.lineinfile module
- **Firewall Configuration**: UFW rules management via shell commands - migrate to community.general.ufw module
- **Fail2ban Configuration**: Template-based jail configuration - migrate to ansible.builtin.template with Jinja2 templates
- **Sysctl Security Tuning**: Security parameter configuration via template - migrate to ansible.posix.sysctl module

### Technical Challenges

- **Ruby Block Logic**: The cache cookbook contains a ruby_block that performs complex Redis configuration file manipulation - will need to be replaced with ansible.builtin.lineinfile or ansible.builtin.replace modules with multiple tasks
- **Git Repository Management**: FastAPI tutorial uses git resource for repository cloning - migrate to ansible.builtin.git module with proper change detection
- **Service Dependencies**: PostgreSQL service must be running before database operations - ensure proper task ordering with handlers and dependencies
- **Template Migration**: ERB templates need conversion to Jinja2 format, particularly nginx.conf.erb and security configuration templates
- **File Permissions**: Complex SSL certificate file permissions (ssl-cert group) - ensure proper ansible.builtin.file module usage with group management

### Migration Order

1. **cache** (low risk, straightforward service configuration)
2. **fastapi-tutorial** (moderate complexity, database dependencies)
3. **nginx-multisite** (high complexity, multiple security configurations and SSL management)

### Assumptions

- Target systems will have internet access for package installation and git repository cloning
- PostgreSQL service installation and configuration approach may differ between Ubuntu and CentOS - cookbook metadata supports both but implementation details not fully examined
- SSL certificate requirements assume development environment with self-signed certificates - production deployment may require different certificate management approach
- UFW firewall is the preferred firewall solution - some environments may require iptables or firewalld instead
- The ruby_block configuration fixes in the Redis setup suggest potential compatibility issues with the redisio cookbook version - root cause analysis needed during migration
- Vagrant development environment configuration not examined - production deployment targets may differ significantly
- Chef Solo configuration suggests single-node deployment - multi-node considerations not addressed in current cookbook structure