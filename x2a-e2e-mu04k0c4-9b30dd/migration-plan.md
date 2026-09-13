# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing caching services, a FastAPI application, and an nginx multi-site reverse proxy with security hardening. The migration involves converting Chef cookbooks to Ansible playbooks and roles, addressing external cookbook dependencies, and migrating security configurations including SSL certificate management and system hardening.

**Estimated Timeline**: 4-6 weeks for complete migration
**Complexity**: Medium - straightforward service configurations with some security complexity
**Team Coordination**: Requires coordination between application, infrastructure, and security teams

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis password authentication, custom log directory creation, configuration file patching via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service management

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening via fail2ban and UFW firewall, and SSH configuration
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, self-signed certificate generation, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security parameters

### Infrastructure Files

- `Berksfile`: Chef cookbook dependency management - defines external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run configuration with run_list and node attributes for site configurations and security settings
- `solo.rb`: Chef Solo configuration file for cookbook and data bag paths
- `Vagrantfile`: Development environment provisioning - will need Ansible equivalent for local testing
- `vagrant-provision.sh`: Shell provisioning script for Vagrant - migration reference for manual steps

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be VM-based deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx configuration
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules for memcached installation and management
- **redisio (~> 7.2.4)**: Replace with ansible.builtin.package, ansible.builtin.template, and ansible.builtin.service modules for Redis configuration and management

### Security Considerations

- **SSL Certificate Management**: Self-signed certificate generation using OpenSSL commands - migrate to ansible.builtin.openssl_* modules or community.crypto collection
- **Hardcoded Credentials**: 
  - Redis password ('redis_secure_password_123') hardcoded in cache cookbook
  - PostgreSQL password ('fastapi_password') hardcoded in fastapi-tutorial cookbook
  - Database connection string with embedded credentials in .env file
- **SSH Hardening**: Root login disable and password authentication disable via direct file modification - migrate to ansible.posix.sshd_config module
- **Firewall Configuration**: UFW rules for HTTP/HTTPS/SSH - migrate to community.general.ufw module
- **Fail2ban Configuration**: Custom jail.local template - migrate to ansible.builtin.template with fail2ban configuration
- **System Security**: sysctl security parameters via template - migrate to ansible.posix.sysctl module

### Technical Challenges

- **Ruby Block Logic**: The cache cookbook contains a ruby_block that performs complex Redis configuration file manipulation - will need to be replaced with ansible.builtin.lineinfile or ansible.builtin.replace modules with multiple tasks
- **Service Dependencies**: PostgreSQL service must be running before database creation in fastapi-tutorial - ensure proper task ordering with handlers and dependencies
- **SSL Certificate Generation**: Self-signed certificate creation with specific ownership and permissions - requires careful migration to maintain security model
- **Multi-site Configuration**: Dynamic site creation based on node attributes - will need Ansible loops and variable structures
- **Git Repository Management**: FastAPI application deployment via git clone - migrate to ansible.builtin.git module with proper change detection

### Migration Order

1. **cache** (low risk, standalone service)
   - Simple service installation and configuration
   - Test Redis and memcached functionality independently
   
2. **fastapi-tutorial** (moderate complexity, database dependencies)
   - PostgreSQL setup and application deployment
   - Validate database connectivity and application startup
   
3. **nginx-multisite** (high complexity, security dependencies)
   - Complex multi-site configuration with SSL
   - Security hardening affects entire system
   - Should be migrated last to avoid breaking other services

### Assumptions

- Target systems will have the same OS versions (Ubuntu 18.04+ or CentOS 7+) as specified in cookbook metadata
- SSL certificates are self-signed for development/testing environments - production may require different certificate management approach
- Database passwords and Redis authentication will be migrated to Ansible Vault for security
- UFW firewall is the preferred firewall solution (not iptables or firewalld)
- Systemd is available for service management on target systems
- Git repository access for FastAPI tutorial application will remain available at the same URL
- Current Chef Solo configuration suggests single-node deployment model - Ansible inventory will reflect similar architecture
- Vagrant development environment will be replaced with equivalent Ansible-based local testing setup
- No external Chef Server dependencies exist (cookbook uses Chef Solo mode)