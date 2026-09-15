# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with 3 cookbooks managing web services, caching infrastructure, and a FastAPI application. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to security configurations, SSL management, and database setup. Estimated timeline: 3-4 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx web server with multi-site SSL configuration, security hardening via fail2ban/UFW, and system-level security controls
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: SSL-enabled virtual hosts for test/ci/status subdomains, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security parameters

**cache**:
- Description: Caching services layer providing both Memcached and Redis with authentication and custom configuration management
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication, custom log directory setup, configuration file post-processing via Ruby block, Memcached integration

**fastapi-tutorial**:
- Description: FastAPI Python web application with PostgreSQL database backend, systemd service management, and virtual environment setup
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment creation, PostgreSQL database and user provisioning, systemd service configuration, environment variable management

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbook versions (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list and node attributes configuration with site definitions and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning configuration
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or cloud-agnostic deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom configuration management
- **ssl_certificate (~> 2.1)**: Replace with community.crypto.* modules for SSL certificate management

### Security Considerations

- **SSH Hardening**: Root login disabled, password authentication disabled - migrate to ansible.posix.sshd_config module
- **Firewall Management**: UFW rules for HTTP/HTTPS/SSH - migrate to community.general.ufw module
- **Fail2ban Configuration**: Custom jail configuration - migrate to community.general.fail2ban module
- **Sysctl Security**: Kernel parameter hardening - migrate to ansible.posix.sysctl module
- **Vault/secrets management**: 
  - Hardcoded credentials identified in cache cookbook (Redis password: 'redis_secure_password_123')
  - Database credentials in fastapi-tutorial cookbook (PostgreSQL password: 'fastapi_password')
  - SSL certificate paths configured but certificates not managed in code
  - Environment variables containing database connection strings
  - Recommend migrating to Ansible Vault for all credential management

### Technical Challenges

- **Ruby Block Logic**: The cache cookbook contains a Ruby block that post-processes Redis configuration files by removing specific lines - this will need to be reimplemented using Ansible's lineinfile module with regex patterns
- **Multi-site SSL Configuration**: Complex template-driven nginx configuration with multiple SSL-enabled virtual hosts requires careful migration to Jinja2 templates and proper certificate management
- **Database Initialization**: PostgreSQL database and user creation uses shell commands that need to be converted to postgresql_* modules with proper idempotency
- **Service Dependencies**: Complex service startup order (PostgreSQL → FastAPI application) requires proper Ansible handler and dependency management
- **Git Repository Management**: Application deployment via git clone needs migration to ansible.builtin.git module with proper change detection

### Migration Order

1. **cache** (low risk, foundational service)
   - Simple package installation and service management
   - Clear external dependencies
   - Good starting point for team familiarity

2. **nginx-multisite** (moderate complexity)
   - Security configurations provide good learning opportunity
   - Template migration practice
   - SSL management complexity

3. **fastapi-tutorial** (high complexity, dependencies)
   - Requires database setup and application deployment
   - Complex systemd service configuration
   - Depends on successful completion of other services

### Assumptions

- SSL certificates are managed externally and placed in the configured paths (/etc/ssl/certs, /etc/ssl/private)
- The FastAPI tutorial repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and stable
- Target systems have internet access for package installation and git repository cloning
- PostgreSQL service configuration beyond basic installation is handled by the application or external configuration management
- The current Chef Solo deployment model will be replaced with Ansible playbook execution
- UFW firewall rules are appropriate for the target environment and don't conflict with existing security policies
- The Ruby block configuration manipulation in the Redis setup is still necessary in the target environment
- Development and production environments will use the same Ansible playbooks with different inventory configurations