# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with nginx reverse proxy, caching services (Redis/Memcached), and a FastAPI application with PostgreSQL backend. The migration involves 3 custom cookbooks with moderate complexity, requiring approximately 4-6 weeks for complete migration including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx reverse proxy with SSL-enabled multi-site configuration, security hardening via fail2ban/UFW, and self-signed certificate generation for development environments
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multiple SSL virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local), fail2ban intrusion prevention, UFW firewall configuration, SSH hardening, sysctl security tuning, self-signed certificate generation

**cache**:
- Description: Caching services configuration with Redis authentication and Memcached, including Redis configuration workarounds for compatibility
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis server with password authentication, Memcached service, custom Redis configuration fixes via ruby_block, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database backend, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service management, environment configuration file generation

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4) and local cookbook paths
- `solo.json`: Chef Solo run list configuration and node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file for cookbook and data bag paths
- `Vagrantfile`: Development environment provisioning configuration
- `vagrant-provision.sh`: Shell script for Vagrant VM provisioning

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (as specified in cookbook metadata), recommend standardizing on Red Hat Enterprise Linux 9 for production
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be VM-based deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks
- **ssl_certificate (~> 2.1)**: Currently commented out, replace with community.crypto.openssl_* modules for certificate management

### Security Considerations

- **Hardcoded credentials**: Redis password "redis_secure_password_123" and PostgreSQL password "fastapi_password" are hardcoded in recipes - migrate to Ansible Vault
- **SSL certificate management**: Self-signed certificates generated via OpenSSL commands - implement proper certificate lifecycle management with Ansible crypto modules
- **SSH security configuration**: Root login disabled, password authentication disabled - maintain these security postures in Ansible
- **Firewall configuration**: UFW rules for SSH, HTTP, HTTPS - migrate to ansible.posix.ufw module
- **Fail2ban configuration**: Intrusion prevention for nginx - migrate to community.general.fail2ban module
- **Sysctl security tuning**: Kernel parameter hardening - migrate to ansible.posix.sysctl module

### Technical Challenges

- **Redis configuration workarounds**: The cache cookbook contains a ruby_block hack to fix Redis configuration file issues - investigate root cause and implement proper Redis configuration in Ansible
- **Complex nginx multi-site setup**: Template-driven virtual host configuration with SSL requires careful migration to Ansible template modules
- **PostgreSQL database initialization**: Database and user creation commands need migration to community.postgresql.* modules with proper idempotency
- **Service dependencies**: FastAPI service depends on PostgreSQL - ensure proper service ordering in Ansible playbooks
- **File permissions and ownership**: Multiple cookbooks manage file permissions for ssl-cert group, www-data user - standardize in Ansible

### Migration Order

1. **cache** (low risk, foundational service) - Redis and Memcached services with minimal external dependencies
2. **fastapi-tutorial** (moderate complexity) - Application deployment with database dependencies but straightforward systemd service
3. **nginx-multisite** (high complexity) - Complex multi-site configuration with SSL, security hardening, and multiple template dependencies

### Assumptions

- Target environments will maintain Ubuntu/CentOS compatibility as specified in cookbook metadata
- Self-signed certificates are acceptable for development environments (production may require proper CA-signed certificates)
- Current hardcoded passwords are development placeholders and will be replaced with proper secret management
- The Redis configuration workarounds indicate compatibility issues that may not exist in newer Redis versions
- Vagrant development environment will be replaced with equivalent Ansible-based local testing
- The commented ssl_certificate cookbook dependency suggests SSL certificate management is handled manually or via the self-signed approach
- PostgreSQL version and configuration requirements are minimal based on the simple database setup in the cookbook
- The nginx external cookbook dependency (~> 12.0) provides basic nginx installation that can be replaced with standard package management
- UFW and fail2ban configurations are suitable for the target security posture and don't require additional hardening
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) will remain accessible during migration