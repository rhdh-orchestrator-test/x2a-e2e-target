# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with caching, security hardening, and SSL-enabled nginx reverse proxy. The migration involves 3 cookbooks with moderate complexity, estimated timeline of 2-3 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis authentication, includes custom Redis configuration fixes and log directory management
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with authentication (password: redis_secure_password_123), memcached integration, custom config file manipulation, log directory creation

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python venv setup, PostgreSQL database/user creation, systemd service management, environment file configuration

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening via fail2ban/UFW, and SSH configuration lockdown
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security parameters

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo configuration with run list and node attributes for site configuration
- `solo.rb`: Chef Solo execution configuration
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support specified in metadata.rb files)
- **Virtual Machine Technology**: Vagrant/VirtualBox (based on Vagrantfile presence)
- **Cloud Platform**: Not specified (local/on-premises deployment)

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks

### Security Considerations

- **Hardcoded credentials**: Redis password (redis_secure_password_123) and PostgreSQL password (fastapi_password) are hardcoded in recipes - migrate to Ansible Vault
- **SSL certificate management**: SSL certificate paths configured but certificate deployment not automated - implement proper certificate management with ansible.builtin.copy or community.crypto modules
- **SSH hardening**: Root login disabled, password authentication disabled - preserve these security configurations in Ansible
- **Firewall configuration**: UFW rules for SSH, HTTP, HTTPS - migrate to community.general.ufw module
- **Fail2ban configuration**: Custom jail.local template - migrate template to Jinja2 format
- **Sysctl security parameters**: Custom security.conf template - migrate to ansible.posix.sysctl module

### Technical Challenges

- **Custom Redis configuration manipulation**: Chef recipe uses ruby_block to modify Redis config file with regex replacements - requires custom Ansible task with ansible.builtin.lineinfile or ansible.builtin.replace modules
- **Multi-site nginx configuration**: Dynamic site creation based on node attributes - implement with Ansible loops and template modules
- **PostgreSQL database initialization**: Chef uses execute resources for database/user creation - migrate to community.postgresql.postgresql_* modules for idempotent database management
- **Git repository management**: FastAPI app deployment via git clone - use ansible.builtin.git module with proper version control
- **Systemd service management**: Custom service file creation and management - use ansible.builtin.systemd and ansible.builtin.template modules

### Migration Order

1. **cache** (low risk, standalone service) - Redis and memcached services with minimal external dependencies
2. **nginx-multisite** (moderate complexity) - Web server configuration with security hardening, depends on SSL certificate availability
3. **fastapi-tutorial** (high complexity) - Application deployment with database dependencies, requires coordination with cache and nginx modules

### Assumptions

- SSL certificates are manually deployed or managed outside of this configuration (certificate paths are configured but deployment is not automated)
- PostgreSQL service is expected to be available on the target system or will be installed as part of system packages
- The FastAPI tutorial application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and the main branch is stable
- Target systems have internet access for package installation and git repository cloning
- The cluster.local domain names (test.cluster.local, ci.cluster.local, status.cluster.local) are properly configured in DNS or /etc/hosts
- Current Chef Solo execution model will be replaced with Ansible playbook execution (no Chef Server infrastructure to migrate)
- Vagrant development environment will be replaced with equivalent Ansible testing setup
- Security hardening requirements (SSH restrictions, firewall rules) remain the same in the target environment