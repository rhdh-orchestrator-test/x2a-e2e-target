# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing web services, caching, and application deployment. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to security configurations, SSL certificate management, and database integration. Estimated timeline: 3-4 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached installation, Redis with password authentication, custom Redis configuration patching, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Python 3 virtual environment, Git repository cloning, PostgreSQL database and user creation, systemd service management, environment configuration

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening, and fail2ban integration
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, self-signed certificate generation, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management - lists external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo configuration with run list and node attributes for site configurations and security settings
- `solo.rb`: Chef Solo configuration file for cookbook paths and execution settings
- `Vagrantfile`: Development environment provisioning - will need Ansible equivalent
- `vagrant-provision.sh`: Shell provisioning script - can be replaced with Ansible provisioner

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox (based on Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be local development environment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom Redis configuration tasks

### Security Considerations

- **SSL Certificate Management**: Self-signed certificate generation using OpenSSL commands - migrate to community.crypto.openssl_* modules
- **Firewall Configuration**: UFW rules for HTTP/HTTPS/SSH - migrate to community.general.ufw module
- **SSH Hardening**: Root login disable, password authentication disable - migrate to ansible.posix.lineinfile or community.general.ssh_config
- **Fail2ban Integration**: Custom jail configuration - migrate to community.general.fail2ban module
- **Sysctl Security Tuning**: Kernel parameter hardening - migrate to ansible.posix.sysctl module
- **Vault/secrets management**: 
  - Hardcoded credentials found in cache cookbook (Redis password: 'redis_secure_password_123')
  - Database credentials in fastapi-tutorial cookbook (PostgreSQL password: 'fastapi_password')
  - SSL certificate generation with hardcoded subject information
  - All credentials should be moved to Ansible Vault for production use

### Technical Challenges

- **Redis Configuration Patching**: The cache cookbook includes a Ruby block that manually edits Redis configuration files to remove specific directives - this will need to be replicated using Ansible's lineinfile module with regex patterns
- **Multi-site SSL Management**: Dynamic SSL certificate generation for multiple sites based on node attributes - will require Ansible loops and conditional logic
- **Database Initialization**: PostgreSQL user and database creation with proper privilege assignment - needs careful handling of idempotency
- **Service Dependencies**: Complex service restart notifications and dependency chains between nginx, fail2ban, and SSL certificate generation
- **File Permissions**: Specific ownership and permission requirements for SSL certificates (ssl-cert group) need careful replication

### Migration Order

1. **cache** (low risk, high value) - Straightforward service installation with known configuration patterns
2. **nginx-multisite** (moderate complexity) - Complex but well-defined security and SSL configurations
3. **fastapi-tutorial** (high complexity, dependencies) - Application deployment with database dependencies and service management

### Assumptions

- The target environment will continue to use Ubuntu/CentOS as specified in cookbook metadata
- Self-signed certificates are acceptable for the target environment (development/testing)
- PostgreSQL and Redis passwords can be moved to Ansible Vault without application code changes
- The current Vagrant-based development workflow will be replaced with Ansible-driven provisioning
- External cookbook dependencies (nginx, memcached, redisio) functionality can be replicated with native Ansible modules
- The Ruby-based Redis configuration patching logic can be accurately converted to Ansible lineinfile operations
- UFW firewall rules and fail2ban configurations are suitable for the target security posture
- Systemd service management approach will remain consistent in the target environment