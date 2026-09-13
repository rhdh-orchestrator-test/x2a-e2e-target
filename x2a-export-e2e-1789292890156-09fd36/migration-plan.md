# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with 3 cookbooks managing web services, caching infrastructure, and a FastAPI application. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to external dependencies and security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx web server with multi-site SSL configuration, security hardening via fail2ban/UFW, and system-level security tuning
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: SSL-enabled virtual hosts for test/ci/status subdomains, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security parameters

**cache**:
- Description: Caching services configuration with memcached and Redis, including authentication and custom Redis configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication, memcached service, custom Redis config file manipulation, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python application deployment with PostgreSQL database, virtual environment setup, and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment, PostgreSQL database and user creation, systemd service configuration, environment file management

### Infrastructure Files

- `Berksfile`: Chef cookbook dependency management with external cookbooks from Chef Supermarket
- `solo.json`: Chef Solo run list and node attributes configuration with site-specific overrides
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Local development environment setup
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be VM-based deployment

## Migration Approach

### Key Dependencies to Address

- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis or custom Redis configuration tasks
- **nginx (~> 12.0)**: Replace with community.general.nginx_* modules or ansible.builtin.template for configuration

### Security Considerations

- **Hardcoded Credentials**: Multiple plaintext passwords found requiring vault migration:
  - Redis password: 'redis_secure_password_123' in cache cookbook
  - PostgreSQL password: 'fastapi_password' in fastapi-tutorial cookbook
  - Database connection string with embedded credentials in .env file
- **SSH Security**: Root login disabled, password authentication disabled - migrate to ansible.posix.sshd_config
- **Firewall Configuration**: UFW rules for HTTP/HTTPS/SSH - migrate to community.general.ufw module
- **Fail2ban**: Jail configuration for nginx protection - migrate to community.general.ini_file or template
- **SSL Certificates**: Certificate and private key path references need secure deployment strategy

### Technical Challenges

- **Redis Configuration Manipulation**: Chef cookbook uses Ruby block to modify Redis config file post-installation - requires custom Ansible task with lineinfile or replace modules
- **PostgreSQL Database Creation**: Chef uses shell commands with sudo -u postgres - migrate to community.postgresql.postgresql_* modules with proper authentication
- **Multi-site Nginx Configuration**: Dynamic site creation based on attributes - requires Ansible loops with template module
- **Systemd Service Management**: Custom service file creation and daemon-reload - use ansible.builtin.systemd module
- **Git Repository Cloning**: FastAPI app deployment from GitHub - use ansible.builtin.git module with proper error handling

### Migration Order

1. **cache** (low risk, standalone caching services)
2. **nginx-multisite** (moderate complexity, security configurations)
3. **fastapi-tutorial** (high complexity, database dependencies, application deployment)

### Assumptions

- Target environments have internet access for package installation and git cloning
- PostgreSQL service can be managed via systemd (not containerized)
- SSL certificates will be provided externally or generated via Let's Encrypt (certificate management not defined in source)
- UFW firewall is acceptable for target environments (no iptables requirements specified)
- Python 3 virtual environments are preferred over system-wide package installation
- Systemd is available for service management (Ubuntu 18.04+/CentOS 7+ assumption)
- Redis and memcached can run on default ports without conflicts
- File permissions and ownership patterns (www-data, redis users) are consistent across target systems
- Git repository https://github.com/dibanez/fastapi_tutorial.git remains accessible and stable
- Chef Supermarket cookbook versions translate to equivalent functionality in Ansible modules