# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages web services, caching layers, and a FastAPI application. The migration involves converting 3 Chef cookbooks to Ansible roles, addressing external dependencies, and maintaining security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers with moderate Chef/Ansible experience.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including authentication, logging, and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis password authentication, custom log directory creation, configuration file patching via Ruby blocks, memcached integration

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service management, environment configuration

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening, and fail2ban protection
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, self-signed certificate generation, fail2ban integration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management - defines external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo configuration with run list and node attributes for site configurations and security settings
- `solo.rb`: Chef Solo execution configuration
- `Vagrantfile`: Development environment provisioning (likely for testing)
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom Redis configuration tasks

### Security Considerations

- **Hardcoded credentials**: Redis password "redis_secure_password_123" and PostgreSQL password "fastapi_password" are hardcoded in recipes - migrate to Ansible Vault
- **SSL certificate management**: Self-signed certificates generated via OpenSSL commands - consider Let's Encrypt integration or proper certificate management
- **SSH hardening**: Root login disabled, password authentication disabled - maintain these security configurations
- **Firewall rules**: UFW configuration for HTTP/HTTPS/SSH - migrate to ansible.posix.ufw module
- **Fail2ban configuration**: Template-based jail configuration - migrate to community.general.fail2ban module
- **Sysctl security tuning**: Custom kernel parameter hardening - migrate to ansible.posix.sysctl module

### Technical Challenges

- **Ruby block workarounds**: The cache cookbook contains Ruby blocks that patch Redis configuration files - need to implement equivalent logic using Ansible lineinfile or replace modules
- **Complex service dependencies**: FastAPI service depends on PostgreSQL being ready - implement proper service ordering and health checks in Ansible
- **Multi-site SSL management**: Dynamic SSL certificate generation for multiple sites - create Ansible loops with proper certificate validation
- **Template migration**: Convert ERB templates (nginx.conf.erb, security.conf.erb, etc.) to Jinja2 templates
- **Git repository management**: FastAPI cookbook clones and manages Git repositories - use ansible.builtin.git module with proper change detection

### Migration Order

1. **cache** (low risk, standalone service) - Redis and memcached configuration with minimal external dependencies
2. **nginx-multisite** (moderate complexity) - Web server with security hardening, depends on SSL certificate generation
3. **fastapi-tutorial** (high complexity) - Application deployment with database dependencies and service management

### Assumptions

- Target environments will maintain Ubuntu/CentOS support as specified in cookbook metadata
- Self-signed certificates are acceptable for development environments (production may require proper CA-signed certificates)
- PostgreSQL and Redis passwords can be migrated to Ansible Vault without changing the actual credential values
- The Ruby block configuration fixes in the Redis cookbook are still necessary and will need equivalent Ansible implementations
- UFW firewall is the preferred firewall solution (rather than iptables or firewalld)
- Systemd is available on target systems for service management
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and the main branch is stable
- Current Chef Solo execution model can be replaced with Ansible playbook execution
- File ownership patterns (www-data, ssl-cert group) are consistent across target environments