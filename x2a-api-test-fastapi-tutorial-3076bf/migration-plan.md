# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages web services, caching layers, and a FastAPI application. The migration involves converting 3 Chef cookbooks to Ansible roles, addressing external dependencies, and maintaining security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

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
- Key Features: Git repository cloning, Python venv creation, PostgreSQL database/user provisioning, systemd service management

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening, and fail2ban protection
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, self-signed certificate generation, fail2ban integration, UFW firewall rules, SSH hardening

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbook versions (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list and node attributes configuration for all three cookbooks
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support specified in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox (based on Vagrantfile presence)
- **Cloud Platform**: Not specified (local development environment)

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks

### Security Considerations

- **Hardcoded credentials**: Redis password "redis_secure_password_123" and PostgreSQL password "fastapi_password" need to be moved to Ansible Vault
- **SSL certificate management**: Self-signed certificate generation needs conversion to ansible.builtin.openssl_* modules
- **SSH hardening**: PermitRootLogin and PasswordAuthentication configurations need conversion to ansible.posix.lineinfile
- **Firewall rules**: UFW commands need conversion to community.general.ufw module
- **Fail2ban configuration**: Template-based jail.local needs conversion to Ansible template module
- **Credential patterns per module**:
  - cache: Redis requirepass in node attributes (1 password)
  - fastapi-tutorial: PostgreSQL user password and database connection string (2 credentials)
  - nginx-multisite: SSL certificate generation (certificate management)

### Technical Challenges

- **Ruby block complexity**: The cache cookbook uses a ruby_block to modify Redis configuration files post-installation, requiring conversion to ansible.builtin.lineinfile or ansible.builtin.replace modules
- **Git repository management**: FastAPI tutorial clones from GitHub, needs conversion to ansible.builtin.git module with proper idempotency
- **Multi-site SSL automation**: Dynamic SSL certificate generation for multiple domains requires Ansible loops and conditional logic
- **Service dependencies**: PostgreSQL must be running before database user creation, requiring proper task ordering and handlers
- **Template variable mapping**: Chef ERB templates need conversion to Jinja2 with attribute-to-variable mapping

### Migration Order

1. **nginx-multisite** (moderate complexity, foundational web server)
2. **cache** (low complexity, independent caching services)
3. **fastapi-tutorial** (high complexity, application deployment with database dependencies)

### Assumptions

- Current Chef cookbooks are functional and represent the desired end state
- External cookbook dependencies (nginx, memcached, redisio) can be replaced with equivalent Ansible modules
- Self-signed certificates are acceptable for the target environment (no Let's Encrypt or CA integration required)
- PostgreSQL installation and configuration are handled by system packages rather than specialized cookbooks
- The ruby_block configuration fixes in the Redis cookbook are still necessary in the target environment
- UFW firewall is the preferred firewall solution (no iptables or firewalld requirements)
- Systemd is available on target systems for service management
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and stable
- Development environment uses Vagrant, but production deployment method is not specified
- No existing Ansible infrastructure or inventory management system is in place