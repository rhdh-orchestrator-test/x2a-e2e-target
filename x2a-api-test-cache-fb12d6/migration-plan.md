# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with nginx reverse proxy, caching services (Redis/Memcached), and a FastAPI Python application with PostgreSQL backend. The migration involves 3 custom cookbooks with moderate complexity, requiring careful attention to SSL certificate management, security hardening configurations, and database credentials. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx reverse proxy with SSL-enabled multi-site hosting, comprehensive security hardening including fail2ban, UFW firewall, SSH hardening, and sysctl security tuning
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: SSL/TLS termination with modern cipher suites, HSTS headers, security headers (CSP, X-Frame-Options), fail2ban intrusion prevention, UFW firewall rules, SSH root login disable, password authentication disable

**cache**:
- Description: Caching services layer providing both Redis and Memcached with authentication and custom configuration management
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis 6379 with password authentication, Memcached service, custom Redis configuration file manipulation, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database backend, virtual environment management, and systemd service integration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service configuration, environment variable management

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Node configuration with run_list and attribute overrides for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file for local cookbook execution
- `Vagrantfile`: Development environment provisioning (requires assessment for Ansible equivalent)
- `vagrant-provision.sh`: Shell provisioning script for Vagrant integration

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be VM-agnostic configuration

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis or ansible.builtin.template for custom Redis configuration
- **External cookbook dependencies**: All external Chef cookbooks need replacement with equivalent Ansible modules or custom tasks

### Security Considerations

- **SSL Certificate Management**: Current implementation references certificate paths (/etc/ssl/certs, /etc/ssl/private) but doesn't show certificate provisioning - migration must address certificate deployment strategy
- **Hardcoded Credentials**: 
  - Redis password "redis_secure_password_123" hardcoded in cache cookbook
  - PostgreSQL credentials "fastapi:fastapi_password" hardcoded in fastapi-tutorial cookbook
  - Database connection string with embedded credentials in .env file
- **SSH Security Configuration**: Automated SSH hardening (root login disable, password auth disable) requires careful testing to avoid lockouts
- **Firewall Rules**: UFW configuration needs validation in Ansible to ensure proper rule ordering and activation
- **Fail2ban Configuration**: Custom jail.local template requires migration to Ansible template module

### Technical Challenges

- **Redis Configuration Manipulation**: The cache cookbook contains a Ruby block that performs regex-based configuration file editing - this complex logic needs reimplementation in Ansible using lineinfile or template modules
- **Multi-site SSL Configuration**: The nginx-multisite cookbook dynamically generates SSL-enabled virtual hosts - requires Ansible loops and conditional SSL certificate validation
- **Service Dependencies**: PostgreSQL must be running before FastAPI application starts - requires proper Ansible handler ordering and service dependency management
- **Git Repository Cloning**: FastAPI cookbook clones from GitHub - migration needs to handle authentication and repository updates properly
- **Systemd Service Management**: Custom systemd unit file creation and daemon-reload coordination requires careful Ansible handler implementation

### Migration Order

1. **cache** (Priority 1: Standalone services, well-defined dependencies, moderate credential management)
2. **nginx-multisite** (Priority 2: Complex security configurations, SSL certificate dependencies, firewall coordination)
3. **fastapi-tutorial** (Priority 3: Application-level service, database dependencies, Git integration complexity)

### Assumptions

- SSL certificates are manually deployed or managed by external process (certificate provisioning method not evident in current Chef code)
- Target environments have internet access for package installation and Git repository cloning
- PostgreSQL installation method assumes package manager availability (apt/yum)
- UFW firewall is acceptable for target environments (may need iptables alternative for some distributions)
- Current hardcoded credentials are acceptable for migration (production environments will need proper secret management)
- Vagrant development workflow will be replaced with equivalent Ansible testing methodology
- The Ruby-based Redis configuration manipulation represents intended configuration state (not temporary workaround)
- Target systems have systemd for service management (no SysV init support evident)
- Git repository https://github.com/dibanez/fastapi_tutorial.git remains accessible and stable
- Multi-platform support (Ubuntu/CentOS) requirement will be maintained in Ansible implementation