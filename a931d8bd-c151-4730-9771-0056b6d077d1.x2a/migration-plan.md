# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing web services, caching infrastructure, and a Python application. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to SSL certificate management, security hardening, and database configuration. Estimated timeline: 3-4 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx web server with multi-site SSL configuration, security hardening via fail2ban/UFW, and system-level security controls
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Self-signed SSL certificate generation, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security parameters, multiple virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local)

**cache**:
- Description: Caching services configuration with Memcached and Redis, including authentication and custom Redis configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication (redis_secure_password_123), custom log directory creation, configuration file manipulation via Ruby blocks, Memcached integration

**fastapi-tutorial**:
- Description: FastAPI Python application deployment with PostgreSQL database, virtual environment setup, and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning from GitHub, Python virtual environment creation, PostgreSQL database and user provisioning, systemd service configuration, environment variable management

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4) and local cookbook paths
- `solo.json`: Chef Solo run list configuration and node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file for cookbook and data bag paths
- `Vagrantfile`: Development environment provisioning with Vagrant
- `vagrant-provision.sh`: Shell script for Vagrant VM provisioning

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be VM-based deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom configuration tasks
- **ssl_certificate (~> 2.1)**: Currently commented out, replace with community.crypto.openssl_* modules for certificate generation

### Security Considerations

- **Hardcoded credentials**: Redis password "redis_secure_password_123" in cache cookbook requires vault integration
- **PostgreSQL credentials**: Database password "fastapi_password" hardcoded in fastapi-tutorial cookbook
- **SSL certificate management**: Self-signed certificates generated via OpenSSL commands need migration to Ansible crypto modules
- **SSH security**: Root login disabled and password authentication disabled via direct file manipulation
- **Firewall configuration**: UFW rules managed through execute resources need conversion to ufw module
- **System hardening**: Sysctl security parameters applied via template and execute resources

### Technical Challenges

- **Ruby block workarounds**: The cache cookbook contains Ruby blocks for Redis configuration file manipulation that need conversion to Ansible lineinfile or template modules
- **Complex SSL setup**: Multi-site SSL certificate generation with proper file permissions and group ownership requires careful Ansible crypto module configuration
- **Service dependencies**: PostgreSQL must be running before database user creation, requiring proper task ordering in Ansible
- **File permission management**: SSL private keys require specific group ownership (ssl-cert) and permissions (640/710)
- **Git repository management**: FastAPI application deployment from GitHub requires idempotent git module usage

### Migration Order

1. **cache** (low risk, high value): Simple service installation with clear external dependencies, good starting point for team familiarity
2. **fastapi-tutorial** (moderate complexity): Database setup and application deployment, moderate complexity with systemd service management
3. **nginx-multisite** (high complexity, dependencies): Complex SSL certificate management, security hardening, and multi-site configuration requiring careful coordination

### Assumptions

- Target environments will maintain Ubuntu/CentOS support as specified in cookbook metadata
- Self-signed certificates are acceptable for development environments (production may require Let's Encrypt or CA-signed certificates)
- Current hardcoded passwords are development-only and will be replaced with proper secret management
- The Ruby block workaround in Redis configuration indicates potential compatibility issues that may not exist in target environments
- Vagrant development environment will be replaced with equivalent Ansible-based local testing
- The commented ssl_certificate cookbook dependency suggests SSL management approach is still being determined
- PostgreSQL version and configuration requirements are minimal based on the simple database setup in fastapi-tutorial
- UFW firewall rules are sufficient for the target security posture
- The fail2ban configuration is standard and doesn't require custom jail rules beyond the template