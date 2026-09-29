# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages web services, caching layers, and a FastAPI application. The migration involves 3 cookbooks with moderate complexity, including security hardening, SSL configuration, and database setup. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx reverse proxy with SSL-enabled multi-site hosting, security hardening via fail2ban/UFW, and system-level security configurations
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multiple SSL virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local), fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security parameters

**cache**:
- Description: Caching services layer providing both Memcached and Redis with authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication, custom log directory setup, configuration file patching via Ruby blocks, Memcached integration

**fastapi-tutorial**:
- Description: FastAPI Python web application with PostgreSQL database backend, systemd service management, and virtual environment setup
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment, PostgreSQL database and user creation, systemd service configuration, environment variable management

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list configuration and node attributes for nginx sites, SSL paths, and security settings
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
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom configuration tasks

### Security Considerations
- SSH hardening configurations: Root login disabled, password authentication disabled
- Firewall management: UFW rules for SSH (22), HTTP (80), HTTPS (443) with default deny policy
- Intrusion detection: fail2ban jail configuration for nginx protection
- System hardening: Custom sysctl security parameters via /etc/sysctl.d/99-security.conf
- Vault/secrets management: 
  - Redis authentication password hardcoded in cache cookbook (redis_secure_password_123)
  - PostgreSQL user password hardcoded in fastapi-tutorial cookbook (fastapi_password)
  - SSL certificate paths configured but certificates not managed by cookbooks
  - Database connection strings with embedded credentials in .env files

### Technical Challenges
- **Ruby Block Workarounds**: The cache cookbook uses Ruby blocks to patch Redis configuration files post-installation, requiring conversion to Ansible lineinfile or replace modules
- **Complex Service Dependencies**: FastAPI service depends on PostgreSQL being fully configured with database and user creation
- **Template Migration**: Multiple ERB templates need conversion to Jinja2 (nginx.conf.erb, security.conf.erb, site.conf.erb, fail2ban.jail.local.erb, sysctl-security.conf.erb)
- **Multi-site SSL Configuration**: Dynamic site creation based on node attributes requires Ansible loops and conditional SSL certificate handling

### Migration Order
1. **cache** (low risk, standalone caching services with clear dependencies)
2. **nginx-multisite** (moderate complexity, security configurations can be tested independently)
3. **fastapi-tutorial** (highest complexity, database dependencies and application deployment)

### Assumptions
- SSL certificates are managed externally and placed in /etc/ssl/certs and /etc/ssl/private directories
- The FastAPI tutorial Git repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and stable
- PostgreSQL service configuration beyond basic installation is handled by system defaults
- The Ruby block configuration fixes in the Redis setup are still necessary and not resolved in newer Redis versions
- UFW and fail2ban packages are available in target system repositories
- The systemd service configuration for FastAPI is appropriate for the target environment
- Node attribute structure in solo.json represents the desired final configuration state