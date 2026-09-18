# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with caching, security hardening, and SSL-enabled nginx reverse proxy. The migration involves 3 cookbooks with moderate complexity, requiring approximately 4-6 weeks for complete migration including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with Memcached and Redis, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached service, Redis with password authentication (redis_secure_password_123), custom Redis configuration cleanup via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment, PostgreSQL database and user creation, systemd service management, environment configuration

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled virtual hosts, security hardening via fail2ban/UFW, and self-signed certificate generation
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, fail2ban intrusion prevention, UFW firewall rules, SSH hardening, sysctl security tuning, self-signed certificate generation

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run configuration with site-specific attributes and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox (based on Vagrantfile presence)
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom Redis configuration tasks

### Security Considerations

- **Hardcoded credentials**: Redis password (redis_secure_password_123) and PostgreSQL credentials (fastapi_password) are embedded in recipes - migrate to Ansible Vault
- **SSL certificate management**: Self-signed certificates generated via OpenSSL commands - consider Let's Encrypt integration or proper certificate management
- **SSH hardening**: Root login disabled, password authentication disabled - preserve these security configurations
- **Firewall rules**: UFW configuration for ports 22, 80, 443 - migrate to ansible.posix.ufw module
- **Fail2ban configuration**: Intrusion prevention via template - migrate to community.general.fail2ban module
- **Sysctl security tuning**: Kernel parameter hardening via template - migrate to ansible.posix.sysctl module

### Technical Challenges

- **Ruby block workarounds**: The cache cookbook contains a ruby_block to fix Redis configuration issues - this custom logic needs to be reimplemented using Ansible's lineinfile or replace modules
- **Complex template dependencies**: Nginx site configuration templates use multiple variables and conditional SSL logic - requires careful Jinja2 template migration
- **Service orchestration**: Multiple services (nginx, postgresql, redis, memcached, fail2ban) with interdependencies - use Ansible handlers and proper task ordering
- **Git repository management**: FastAPI application deployment via git clone - migrate to ansible.builtin.git module with proper change detection
- **Python virtual environment**: Complex pip and venv management - use ansible.builtin.pip module with virtualenv parameters

### Migration Order

1. **cache** (low risk, foundational service) - Memcached and Redis setup with authentication
2. **fastapi-tutorial** (moderate complexity) - Application deployment with database dependencies
3. **nginx-multisite** (high complexity) - Multi-site SSL proxy with security hardening and template complexity

### Assumptions

- The target environment will maintain the same OS support (Ubuntu 18.04+, CentOS 7+) as specified in cookbook metadata
- Self-signed certificates are acceptable for the target environment (production deployments may require proper CA-signed certificates)
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and compatible
- Database credentials and Redis passwords will be migrated to Ansible Vault for security
- The three-site configuration (test.cluster.local, ci.cluster.local, status.cluster.local) represents the complete scope of virtual hosts
- UFW firewall rules are appropriate for the target environment (some environments may use iptables or other firewall solutions)
- The ruby_block workaround in the Redis configuration indicates potential compatibility issues that may need investigation in the target Ansible environment
- Systemd is available on target systems for service management (implied by the FastAPI systemd service configuration)