# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages web services, caching layers, and application deployment. The migration involves converting 3 Chef cookbooks to Ansible roles, addressing external dependencies, and maintaining security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers with moderate Chef/Ansible experience.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including authentication, logging, and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication, memcached integration, custom Redis config patching, log directory management

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

- `Berksfile`: Chef dependency management - defines external cookbook dependencies (nginx, memcached, redisio)
- `solo.json`: Chef Solo configuration with run list and node attributes for site configuration and security settings
- `solo.rb`: Chef Solo configuration file for local cookbook execution
- `Vagrantfile`: Development environment provisioning (likely for testing)
- `vagrant-provision.sh`: Shell script for Vagrant VM provisioning

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible-role-nginx or community.general.nginx modules
- **memcached (~> 6.0)**: Replace with ansible-memcached role or package/service modules
- **redisio (~> 7.2.4)**: Replace with ansible-redis role or custom Redis configuration tasks

### Security Considerations

- **Hardcoded Credentials**: Multiple plaintext passwords found requiring vault migration:
  - Redis password: `redis_secure_password_123` in cache cookbook
  - PostgreSQL password: `fastapi_password` in fastapi-tutorial cookbook
  - Database credentials in environment files
- **SSL Certificate Management**: Self-signed certificate generation for development environments - consider Let's Encrypt integration for production
- **SSH Hardening**: Root login disabled, password authentication disabled - maintain these security settings
- **Firewall Configuration**: UFW rules for HTTP/HTTPS/SSH - migrate to ansible.posix.firewalld or ufw modules
- **Fail2ban Integration**: Jail configuration for nginx protection - migrate to fail2ban Ansible role
- **Sysctl Security Tuning**: Kernel parameter hardening - migrate to ansible.posix.sysctl module

### Technical Challenges

- **Custom Redis Configuration Patching**: The cache cookbook includes a Ruby block that manually edits Redis config files to remove specific directives - this will need to be reimplemented using Ansible's lineinfile or replace modules
- **Multi-site SSL Certificate Generation**: Complex logic for generating per-site SSL certificates with proper file permissions and ownership - requires careful template and file module coordination
- **Service Dependencies**: FastAPI service depends on PostgreSQL being ready - implement proper service ordering with Ansible handlers
- **File Permission Management**: Complex ownership patterns (www-data, ssl-cert group) need careful mapping to Ansible file modules

### Migration Order

1. **cache** (low risk, standalone caching services)
2. **nginx-multisite** (moderate complexity, security-focused)
3. **fastapi-tutorial** (high complexity, application deployment with database dependencies)

### Assumptions

- Development environment uses self-signed certificates (production may require different SSL strategy)
- PostgreSQL installation assumes local database server (may need adjustment for external databases)
- UFW firewall is the preferred solution (some environments may use iptables or firewalld)
- Redis and memcached run on default ports without clustering requirements
- FastAPI application repository remains accessible at the specified GitHub URL
- System users (www-data, ssl-cert group) exist or can be created during migration
- Chef Solo execution model translates to Ansible playbook execution (no Chef Server dependencies)
- Current hardcoded passwords are acceptable for development but will need vault integration for production