# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages web services, caching layers, and application deployment. The migration involves converting 3 Chef cookbooks to Ansible playbooks, with moderate complexity due to security configurations, SSL management, and database integration. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication, memcached integration, custom Redis configuration patching via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service management

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening, and fail2ban integration
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, fail2ban jail configuration, UFW firewall rules, SSH security hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list configuration and attribute overrides for site configurations and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support specified in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx configuration
- **memcached (~> 6.0)**: Replace with community.general.memcached module or direct package installation
- **redisio (~> 7.2.4)**: Replace with community.general.redis module and custom configuration management

### Security Considerations

- **Hardcoded Credentials**: Multiple plaintext passwords found requiring vault migration:
  - Redis password: 'redis_secure_password_123' in cache cookbook
  - PostgreSQL password: 'fastapi_password' in fastapi-tutorial cookbook
  - Database connection strings with embedded credentials in .env files
- **SSL Certificate Management**: SSL certificate paths configured but certificate provisioning method unclear - needs investigation for Let's Encrypt or manual certificate deployment
- **SSH Hardening**: Root login disabled, password authentication disabled - migrate to ansible.posix.sshd_config module
- **Firewall Configuration**: UFW rules for HTTP/HTTPS/SSH - migrate to community.general.ufw module
- **Fail2ban Integration**: Custom jail configuration for nginx protection - migrate to community.general.fail2ban module
- **Sysctl Security Tuning**: Kernel parameter hardening via sysctl - migrate to ansible.posix.sysctl module

### Technical Challenges

- **Ruby Block Logic**: Cache cookbook contains complex Ruby code for Redis configuration patching that needs conversion to Ansible tasks with lineinfile or replace modules
- **Service Dependencies**: PostgreSQL service must be running before database user creation - requires proper task ordering and handlers
- **Multi-site Configuration**: Dynamic site creation based on attributes requires Ansible loops and template generation
- **Git Repository Management**: FastAPI application deployment via git clone needs conversion to ansible.builtin.git module with proper change detection
- **Virtual Environment Management**: Python venv creation and pip installation requires ansible.builtin.pip module with virtualenv support
- **Systemd Service Management**: Custom service file creation and daemon-reload requires ansible.builtin.systemd module

### Migration Order

1. **nginx-multisite** (moderate complexity, foundational web infrastructure)
2. **cache** (low-moderate complexity, independent caching services)
3. **fastapi-tutorial** (high complexity, application deployment with database dependencies)

### Assumptions

- SSL certificates are manually managed or provided externally (no automated certificate provisioning detected in cookbooks)
- The target environment has internet access for package installation and git repository cloning
- PostgreSQL installation method is via system packages rather than custom compilation
- Redis configuration patching in the cache cookbook is still necessary in the target environment
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and the 'main' branch is stable
- UFW is the preferred firewall solution for the target Ubuntu systems
- The multi-site configuration pattern (test.cluster.local, ci.cluster.local, status.cluster.local) will be maintained
- Systemd is available on target systems for service management
- The www-data user and group exist on target systems for nginx file ownership
- Development environment provisioning via Vagrant is not required in the Ansible migration (production focus)