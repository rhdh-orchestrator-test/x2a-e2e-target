# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with caching, security hardening, and SSL-enabled nginx reverse proxy. The migration involves 3 cookbooks with moderate complexity, estimated timeline of 2-3 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including authentication, logging, and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis authentication (requirepass), custom log directory creation, configuration file patching via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python venv creation, PostgreSQL database/user provisioning, systemd service management

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening (fail2ban, UFW firewall), and self-signed certificate generation
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list and node attributes configuration for all three cookbooks
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support specified in metadata.rb files)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be VM-based deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx configuration
- **memcached (~> 6.0)**: Replace with community.general.memcached or direct package installation
- **redisio (~> 7.2.4)**: Replace with community.general.redis or ansible.builtin.package with custom configuration

### Security Considerations

- **Hardcoded credentials**: Redis password "redis_secure_password_123" and PostgreSQL password "fastapi_password" are hardcoded in recipes - migrate to Ansible Vault
- **SSL certificate management**: Self-signed certificates generated via OpenSSL commands - consider ansible.builtin.openssl_* modules or external CA integration
- **SSH hardening**: Root login disabled, password authentication disabled - migrate to ansible.posix.sshd_config module
- **Firewall configuration**: UFW rules for SSH, HTTP, HTTPS - migrate to community.general.ufw module
- **Fail2ban configuration**: Custom jail.local template - migrate to ansible.builtin.template with fail2ban configuration
- **Sysctl security tuning**: Custom security parameters - migrate to ansible.posix.sysctl module

### Technical Challenges

- **Ruby block configuration patching**: The cache cookbook uses ruby_block to modify Redis configuration files post-installation - requires conversion to Ansible lineinfile or replace modules with proper regex patterns
- **Multi-site SSL certificate generation**: Dynamic certificate creation for multiple domains requires Ansible loops and conditional logic
- **Service dependency management**: PostgreSQL must be running before database creation, nginx reload dependencies on configuration changes - requires proper Ansible handlers and task ordering
- **Git repository management**: FastAPI application deployment from Git requires ansible.builtin.git module with proper change detection
- **Python virtual environment**: Complex pip installation within venv requires ansible.builtin.pip module with virtualenv parameters

### Migration Order

1. **cache** (low risk, standalone service) - Redis and memcached services with minimal external dependencies
2. **nginx-multisite** (moderate complexity) - Web server configuration with security hardening, depends on SSL certificate generation
3. **fastapi-tutorial** (high complexity) - Application deployment with database dependencies, systemd service management, and Git integration

### Assumptions

- Target environments will maintain Ubuntu/CentOS compatibility as specified in Chef metadata
- Self-signed certificates are acceptable for development/internal use (production may require CA-signed certificates)
- PostgreSQL installation method (package vs. source) is flexible and can use distribution packages
- Redis configuration patching via ruby_block indicates potential upstream package issues that may need investigation
- UFW firewall is the preferred firewall solution (vs. iptables or firewalld)
- Systemd is available on target systems for service management
- Git repository access (https://github.com/dibanez/fastapi_tutorial.git) will remain available during migration
- Chef Solo configuration suggests single-node deployments rather than multi-node orchestration
- Development workflow using Vagrant can be replaced with molecule or direct Ansible testing