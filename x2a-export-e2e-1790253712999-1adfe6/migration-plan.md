# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with caching, security hardening, and SSL-enabled nginx reverse proxy. The migration involves 3 cookbooks with moderate complexity, estimated timeline of 2-3 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis authentication, includes Redis log directory setup and configuration file patching
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached integration, Redis with password authentication (redis_secure_password_123), custom Redis configuration patching, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service management, environment configuration file

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening via fail2ban and UFW firewall, SSH configuration lockdown
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, self-signed certificate generation, fail2ban integration, UFW firewall rules, SSH security hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list configuration and node attributes for site definitions and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support specified in metadata.rb files)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be VM-agnostic configuration

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom Redis configuration tasks

### Security Considerations

- **Hardcoded credentials**: Redis password "redis_secure_password_123" and PostgreSQL password "fastapi_password" are hardcoded in recipes - migrate to Ansible Vault
- **SSL certificate management**: Self-signed certificates generated via OpenSSL commands - consider Let's Encrypt integration with community.crypto collection
- **SSH security configuration**: Root login disabled, password authentication disabled - maintain with ansible.posix.sshd_config module
- **Firewall rules**: UFW configuration for HTTP/HTTPS/SSH - migrate to community.general.ufw module
- **Fail2ban configuration**: Custom jail.local template - migrate to community.general.fail2ban module
- **Sysctl security tuning**: Custom security parameters - migrate to ansible.posix.sysctl module

### Technical Challenges

- **Redis configuration patching**: Complex ruby_block that modifies Redis config file post-installation requires custom Ansible task with lineinfile or replace modules
- **Multi-site SSL certificate generation**: Dynamic certificate creation per site needs loop-based certificate generation with community.crypto.openssl_* modules
- **PostgreSQL database initialization**: Database and user creation commands need idempotent conversion using community.postgresql.* modules
- **Git repository management**: FastAPI app deployment from Git requires ansible.builtin.git module with proper change detection
- **Systemd service template**: Custom service file creation needs ansible.builtin.template with systemd handler integration

### Migration Order

1. **cache** (low risk, standalone service) - Redis and memcached services with minimal external dependencies
2. **fastapi-tutorial** (moderate complexity) - Application deployment with database dependencies but isolated functionality  
3. **nginx-multisite** (high complexity, security-critical) - Complex multi-site configuration with security hardening that affects system-wide settings

### Assumptions

- Target environments will maintain Ubuntu/CentOS compatibility as specified in Chef metadata
- Self-signed certificates are acceptable for development; production may require Let's Encrypt or external CA integration
- PostgreSQL and Redis passwords can be migrated to Ansible Vault without application code changes
- UFW firewall is the preferred firewall solution (vs iptables) on target systems
- Systemd is available on target systems for service management
- Git repository access (https://github.com/dibanez/fastapi_tutorial.git) will remain available during migration
- Current Chef Solo execution model can be replaced with Ansible playbook execution
- File ownership patterns (www-data, ssl-cert group) are consistent across target environments
- Python 3 virtual environment approach is preferred over system-wide package installation