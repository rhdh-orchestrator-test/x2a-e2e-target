# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages web services, caching layers, and a FastAPI application. The migration involves 3 cookbooks with moderate complexity, including security hardening, SSL certificate management, and database configuration. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx web server with multi-site SSL configuration, security hardening (fail2ban, UFW firewall), and SSH hardening
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multiple SSL-enabled virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local), self-signed certificate generation, fail2ban intrusion prevention, UFW firewall rules, SSH security configuration, sysctl kernel parameter tuning

**cache**:
- Description: Caching services configuration with both Memcached and Redis, including authentication and custom Redis configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached service, Redis with password authentication (redis_secure_password_123), custom Redis configuration patching via ruby_block, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database backend, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Python 3 virtual environment, Git repository cloning from GitHub, PostgreSQL database and user creation, systemd service management, environment configuration file

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list configuration and node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support specified in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (based on Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or cloud-agnostic deployment

## Migration Approach

### Key Dependencies to Address
- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks

### Security Considerations
- **Hardcoded credentials**: Redis password (redis_secure_password_123) and PostgreSQL password (fastapi_password) are hardcoded in recipes - migrate to Ansible Vault
- **SSL certificate management**: Self-signed certificate generation needs migration to ansible.builtin.openssl_* modules
- **SSH hardening**: Root login disable and password authentication disable configurations need careful migration
- **Firewall rules**: UFW firewall configuration (SSH, HTTP, HTTPS) requires ufw module or iptables equivalent
- **Fail2ban configuration**: Intrusion prevention system configuration via template needs migration
- **Sysctl security parameters**: Kernel security tuning via template requires ansible.posix.sysctl module
- **Credential types per module**:
  - nginx-multisite: SSL private keys, no database credentials
  - cache: Redis authentication password
  - fastapi-tutorial: PostgreSQL database credentials, GitHub repository access (public)

### Technical Challenges
- **Ruby block workaround**: The cache cookbook contains a Ruby block hack to fix Redis configuration - this custom logic needs to be reimplemented as Ansible tasks with lineinfile or replace modules
- **Multi-site SSL management**: Dynamic SSL certificate generation for multiple sites requires loop-based certificate creation in Ansible
- **Service dependencies**: PostgreSQL must be running before FastAPI application starts - requires proper task ordering and handlers
- **Template migration**: ERB templates (nginx.conf.erb, security.conf.erb, site.conf.erb, etc.) need conversion to Jinja2 format
- **Git repository management**: FastAPI tutorial cloning and virtual environment management requires ansible.builtin.git and ansible.builtin.pip modules

### Migration Order
1. **cache** (low risk, standalone service, clear dependencies)
2. **fastapi-tutorial** (moderate complexity, database dependencies, but isolated application)
3. **nginx-multisite** (high complexity, security configurations, SSL management, depends on other services being available)

### Assumptions
- SSL certificates are self-signed for development/testing environments - production deployment may require Let's Encrypt or CA-signed certificates
- PostgreSQL installation and initial configuration is handled by system packages - no custom PostgreSQL tuning or replication setup
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and the main branch is stable
- UFW firewall is the preferred firewall solution - iptables rules may need adjustment for different distributions
- Redis configuration "hack" in ruby_block is still necessary - the specific configuration lines being removed may need validation
- Development environment uses Vagrant - production deployment method is not specified
- All services run on a single server - no distributed or containerized deployment patterns
- The nginx sites (test.cluster.local, ci.cluster.local, status.cluster.local) are internal/development domains
- System user 'www-data' exists for nginx file ownership (Ubuntu/Debian assumption)
- Python 3 virtual environment approach is preferred over system-wide package installation