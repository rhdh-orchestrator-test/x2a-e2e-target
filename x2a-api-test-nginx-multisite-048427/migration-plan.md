# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages web services, caching layers, and a FastAPI application with comprehensive security hardening. The migration involves 3 cookbooks with moderate complexity, requiring approximately 4-6 weeks for a complete migration including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
All module paths have been verified from the repository tree and confirmed via file exploration.

- **cache**:
    - Description: Caching services configuration with memcached and Redis, including authentication and custom configuration fixes
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, memcached integration, custom Redis configuration patching, log directory management

- **fastapi-tutorial**:
    - Description: FastAPI Python web application with PostgreSQL database backend, virtual environment management, and systemd service configuration
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service management, environment configuration

- **nginx-multisite**:
    - Description: Nginx reverse proxy with SSL-enabled multi-domain hosting, security hardening, and firewall configuration
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-domain SSL configuration, fail2ban integration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management - defines external cookbook dependencies (nginx, memcached, redisio) and local cookbook paths
- `solo.json`: Chef Solo configuration with run list and node attributes - contains site configurations, SSL paths, and security settings
- `solo.rb`: Chef Solo runtime configuration
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or cloud-agnostic deployment

## Migration Approach

### Key Dependencies to Address
- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx configuration
- **memcached (~> 6.0)**: Replace with community.general.memcached module or custom package/service tasks
- **redisio (~> 7.2.4)**: Replace with community.general.redis module and custom configuration management

### Security Considerations
- **Hardcoded credentials**: Redis password ('redis_secure_password_123') and PostgreSQL credentials ('fastapi_password') are embedded in recipes - migrate to Ansible Vault
- **SSH hardening**: Root login disabled, password authentication disabled - implement via ansible.posix.sshd_config module
- **Firewall configuration**: UFW rules for HTTP/HTTPS/SSH - migrate to community.general.ufw module
- **Fail2ban integration**: Jail configuration for nginx protection - use community.general.fail2ban module
- **SSL certificate management**: Certificate and private key paths configured but certificates not managed by Chef - implement proper certificate deployment in Ansible
- **Sysctl security tuning**: Kernel parameter hardening via template - migrate to ansible.posix.sysctl module

### Technical Challenges
- **Redis configuration patching**: Chef uses ruby_block to manually edit Redis config files post-installation - requires custom Ansible tasks with lineinfile or template modules
- **Multi-domain SSL setup**: Complex nginx configuration with per-site SSL certificates - implement with Jinja2 templates and certificate management
- **PostgreSQL database initialization**: Database and user creation via shell commands - migrate to community.postgresql modules for idempotent database management
- **Git repository management**: FastAPI app deployment via git clone - use ansible.builtin.git module with proper change detection
- **Python virtual environment**: Manual venv creation and pip installation - leverage ansible.builtin.pip module with virtualenv support

### Migration Order
1. **cache** (moderate complexity, no dependencies on other cookbooks)
2. **fastapi-tutorial** (moderate complexity, database setup, independent application)
3. **nginx-multisite** (high complexity, security configurations, potential reverse proxy for FastAPI)

### Assumptions
- SSL certificates are managed externally and placed in the configured paths (/etc/ssl/certs and /etc/ssl/private)
- The FastAPI tutorial repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and stable
- PostgreSQL service is expected to be managed by the system package manager
- The target environment has internet access for package installation and git repository cloning
- UFW is the preferred firewall solution (Ubuntu-centric assumption)
- The 'www-data' user exists for nginx file ownership (Ubuntu/Debian assumption)
- Redis and memcached will run with default system user configurations
- The migration will maintain the same multi-site domain structure (test.cluster.local, ci.cluster.local, status.cluster.local)
- Systemd is available for service management (modern Linux distributions)