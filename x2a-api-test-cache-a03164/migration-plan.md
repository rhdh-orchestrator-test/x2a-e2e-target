# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages web services, caching layers, and a FastAPI application. The migration involves converting 3 Chef cookbooks to Ansible roles, addressing external cookbook dependencies, and migrating security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers, with moderate complexity due to SSL certificate management and database configurations.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including authentication and custom Redis configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis password authentication, custom log directory creation, configuration file patching via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python venv creation, PostgreSQL database and user provisioning, systemd service management

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening, and fail2ban integration
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, self-signed certificate generation, fail2ban jail configuration, UFW firewall rules, SSH hardening

### Infrastructure Files

- `Berksfile`: Chef cookbook dependency management - defines external cookbook versions (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run configuration with site-specific attributes and security settings
- `solo.rb`: Chef Solo configuration file for local cookbook execution
- `Vagrantfile`: Development environment provisioning (requires review for Ansible conversion)
- `vagrant-provision.sh`: Shell provisioning script for Vagrant integration

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be local/on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom Redis configuration tasks

### Security Considerations

- **Hardcoded Credentials**: Multiple plaintext passwords identified requiring Ansible Vault migration:
  - Redis password: `redis_secure_password_123` in cache cookbook
  - PostgreSQL password: `fastapi_password` in fastapi-tutorial cookbook
  - Database connection strings with embedded credentials in .env files
- **SSL Certificate Management**: Self-signed certificate generation via OpenSSL commands needs conversion to community.crypto.openssl_* modules
- **SSH Hardening**: Root login disable and password authentication disable via sed commands require conversion to ansible.posix.sshd_config module
- **Firewall Configuration**: UFW commands need migration to community.general.ufw module
- **Fail2ban Integration**: Template-based jail.local configuration requires Ansible template conversion

### Technical Challenges

- **Ruby Block Logic**: The cache cookbook contains complex Ruby code for Redis configuration file manipulation that needs conversion to Ansible lineinfile or replace modules
- **Service Dependencies**: PostgreSQL service must be running before database user creation - requires proper Ansible task ordering with handlers
- **Multi-site SSL**: Dynamic SSL certificate generation for multiple domains requires Ansible loops and conditional logic
- **Git Repository Management**: FastAPI application deployment via git clone needs conversion to ansible.builtin.git module with proper change detection
- **Systemd Service Creation**: Custom systemd unit file creation requires template conversion and systemctl daemon-reload handling

### Migration Order

1. **cache** (low risk, foundational service)
   - Straightforward package installation and service management
   - Redis configuration complexity can be addressed incrementally
2. **nginx-multisite** (moderate complexity)
   - SSL certificate generation and multi-site configuration
   - Security hardening features are well-defined
3. **fastapi-tutorial** (high complexity, application dependencies)
   - Database provisioning and application deployment
   - Depends on proper Python environment and Git repository management

### Assumptions

- Target environments have internet access for package installation and Git repository cloning
- PostgreSQL installation method (package vs. container) not explicitly defined - assuming package-based installation
- SSL certificate requirements unclear - migration assumes continued use of self-signed certificates for development
- Fail2ban jail configuration templates not examined - assuming standard SSH protection rules
- Redis configuration "HACK" suggests upstream cookbook issues - root cause analysis needed for proper Ansible implementation
- UFW firewall rules assume standard HTTP/HTTPS/SSH ports - custom port requirements not specified
- Systemd service user (currently root) may need security review for production deployment
- Database backup and recovery procedures not defined in current Chef implementation
- Log rotation and monitoring configurations not present - may need addition during Ansible migration