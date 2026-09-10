# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing web services, caching infrastructure, and a FastAPI application. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to security configurations, SSL certificate management, and database setup. Estimated timeline: 3-4 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis password authentication, custom log directory creation, configuration file patching via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment setup, and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment, PostgreSQL database and user creation, systemd service configuration

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening, and fail2ban integration
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo configuration with run list and node attributes for site configurations and security settings
- `solo.rb`: Chef Solo execution configuration
- `Vagrantfile`: Development environment provisioning (requires review for Ansible equivalent)
- `vagrant-provision.sh`: Shell provisioning script for Vagrant integration

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be local/on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom Redis configuration tasks

### Security Considerations

- **Hardcoded Credentials**: Multiple instances requiring Ansible Vault migration:
  - Redis password: `redis_secure_password_123` in cache cookbook
  - PostgreSQL credentials: `fastapi:fastapi_password` in fastapi-tutorial cookbook
  - Database connection strings in environment files
- **SSL Certificate Management**: Self-signed certificate generation for development environments needs conversion to ansible.builtin.openssl_* modules
- **SSH Hardening**: Root login disable and password authentication disable configurations
- **Firewall Configuration**: UFW rules for HTTP/HTTPS/SSH access
- **Fail2ban Integration**: Jail configuration for nginx protection
- **Sysctl Security Tuning**: Kernel parameter hardening configurations

### Technical Challenges

- **Ruby Block Logic**: The cache cookbook contains complex Ruby logic for Redis configuration file manipulation that needs conversion to Ansible lineinfile or template modules
- **Multi-Site SSL**: Complex SSL certificate generation and nginx site configuration loop requires careful Ansible templating
- **Database Initialization**: PostgreSQL user and database creation with proper privilege assignment needs idempotent Ansible tasks
- **Service Dependencies**: Proper ordering of nginx, postgresql, redis, and application services
- **File Permissions**: SSL certificate file permissions and ownership (ssl-cert group) require careful mapping

### Migration Order

1. **cache** (moderate complexity, standalone service)
2. **nginx-multisite** (high complexity due to SSL and security configurations, but foundational)
3. **fastapi-tutorial** (depends on database setup, application deployment complexity)

### Assumptions

- Target environments will maintain Ubuntu/CentOS compatibility as specified in cookbook metadata
- Self-signed certificates are acceptable for development (production may require Let's Encrypt or CA-signed certificates)
- Current hardcoded passwords are development/testing credentials and will be replaced with Ansible Vault variables
- PostgreSQL and Redis services will be managed locally on the same hosts (no external database clusters)
- UFW firewall is the preferred firewall solution (vs iptables or firewalld)
- Systemd is available for service management on target systems
- Git repository access for FastAPI tutorial code will remain available during migration
- Current Chef Solo execution model will be replaced with Ansible playbook execution
- Vagrant development environment setup will be maintained with Ansible provisioner