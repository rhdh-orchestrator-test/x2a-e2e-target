# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with nginx reverse proxy, caching services (Redis/Memcached), and a FastAPI application with PostgreSQL backend. The migration involves 3 custom cookbooks with moderate complexity, requiring approximately 4-6 weeks for complete migration including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx reverse proxy with SSL-enabled multi-site hosting, security hardening via fail2ban/UFW firewall, and self-signed certificate generation for development environments
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multiple SSL virtual hosts (test/ci/status subdomains), fail2ban intrusion prevention, UFW firewall configuration, SSH hardening, sysctl security tuning, self-signed certificate generation

**cache**:
- Description: Caching services configuration providing both Redis and Memcached with authentication and custom Redis configuration management
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis 6379 with password authentication, Memcached service, custom Redis configuration file manipulation, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database backend, systemd service management, and virtual environment setup
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment creation, PostgreSQL database and user provisioning, systemd service configuration, environment variable management

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list configuration and node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file for cookbook paths and execution settings
- `Vagrantfile`: Development environment provisioning for local testing
- `vagrant-provision.sh`: Shell script for Vagrant VM provisioning automation

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (based on Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be platform-agnostic configuration

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis or ansible.builtin.template for custom Redis configuration
- **ssl_certificate (~> 2.1)**: Replace with community.crypto.openssl_* modules for certificate generation

### Security Considerations

- **Hardcoded credentials**: Redis password ('redis_secure_password_123') and PostgreSQL credentials ('fastapi_password') are embedded in recipe code - migrate to Ansible Vault
- **SSL certificate management**: Self-signed certificates generated via OpenSSL commands - migrate to community.crypto collection for proper certificate lifecycle management
- **SSH security configuration**: Root login disable and password authentication disable configured via sed commands - migrate to ansible.posix.sshd_config module
- **Firewall rules**: UFW firewall rules managed via execute resources - migrate to community.general.ufw module
- **Fail2ban configuration**: Template-based jail configuration - migrate to ansible.builtin.template with proper handlers
- **Credential types per module**:
  - nginx-multisite: SSL certificate paths, SSH configuration
  - cache: Redis authentication password
  - fastapi-tutorial: PostgreSQL database credentials, application environment variables

### Technical Challenges

- **Custom Redis configuration manipulation**: The cache cookbook uses Ruby blocks to modify Redis config files post-installation - requires careful translation to Ansible lineinfile or template modules
- **Multi-site SSL certificate generation**: Dynamic certificate creation per site requires loop-based Ansible tasks with proper certificate validation
- **Service dependency management**: FastAPI service depends on PostgreSQL being ready - requires Ansible handlers and proper task ordering
- **Git repository synchronization**: FastAPI cookbook clones and syncs git repositories - migrate to ansible.builtin.git module with proper change detection
- **Python virtual environment management**: Complex pip installation within venv requires ansible.builtin.pip module with proper virtualenv configuration

### Migration Order

1. **cache** (low risk, foundational service): Simple service installation with well-defined external dependencies
2. **fastapi-tutorial** (moderate complexity): Application deployment with database dependencies but isolated functionality  
3. **nginx-multisite** (high complexity, multiple dependencies): Complex multi-site configuration with security hardening that depends on other services being available

### Assumptions

- Target environments will maintain Ubuntu/CentOS compatibility as specified in cookbook metadata
- Self-signed certificates are acceptable for development environments (production may require Let's Encrypt or CA-signed certificates)
- Current hardcoded passwords are acceptable for migration (should be moved to Ansible Vault post-migration)
- PostgreSQL and Redis services will continue to run on the same hosts as the applications
- The FastAPI tutorial application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and stable
- Vagrant-based development workflow will be maintained or replaced with equivalent Ansible-based local testing
- Current firewall rules (SSH, HTTP, HTTPS) are sufficient and no additional ports need to be opened
- The nginx sites configuration (test.cluster.local, ci.cluster.local, status.cluster.local) represents the complete set of required virtual hosts