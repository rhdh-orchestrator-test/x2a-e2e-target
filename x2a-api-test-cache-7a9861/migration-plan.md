# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with caching, security hardening, and SSL-enabled nginx reverse proxy. The migration involves 3 cookbooks with moderate complexity, estimated timeline of 3-4 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx reverse proxy with SSL termination for multiple subdomains (test.cluster.local, ci.cluster.local, status.cluster.local), security hardening with fail2ban, UFW firewall, and SSH configuration
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, fail2ban integration, UFW firewall rules, SSH hardening, sysctl security tuning, static file serving

**cache**:
- Description: Caching services configuration with memcached and Redis, including authentication and custom Redis configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication, memcached integration, custom Redis config patching, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment, PostgreSQL database and user creation, systemd service management, environment configuration

### Infrastructure Files

- `Berksfile`: Chef dependency management - defines external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo configuration with run list and node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file for local cookbook execution
- `Vagrantfile`: Development environment provisioning (requires review for Ansible equivalent)
- `vagrant-provision.sh`: Shell provisioning script for Vagrant integration

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be local/on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom configuration tasks

### Security Considerations

- **Hardcoded Credentials**: Multiple plaintext passwords identified requiring Ansible Vault migration:
  - Redis password: 'redis_secure_password_123' in cache cookbook
  - PostgreSQL password: 'fastapi_password' in fastapi-tutorial cookbook
  - Database connection strings with embedded credentials in .env files
- **SSL Certificate Management**: SSL certificate paths configured but certificate provisioning method unclear - requires investigation of certificate deployment strategy
- **SSH Hardening**: Root login disabled, password authentication disabled - migrate to ansible.posix.sshd_config module
- **Firewall Configuration**: UFW rules for HTTP/HTTPS/SSH - migrate to community.general.ufw module
- **Fail2ban Integration**: Jail configuration via templates - migrate to community.general.fail2ban module
- **Sysctl Security Tuning**: Kernel parameter hardening via templates - migrate to ansible.posix.sysctl module

### Technical Challenges

- **Custom Redis Configuration Patching**: The cache cookbook includes a Ruby block that manually edits Redis configuration files to remove specific directives - this will require custom Ansible tasks with lineinfile or replace modules
- **Multi-site SSL Configuration**: Complex nginx site configuration with SSL for multiple subdomains requires careful template migration and certificate management strategy
- **Database Initialization**: PostgreSQL user and database creation with privilege grants needs idempotent Ansible equivalent using community.postgresql modules
- **Git Repository Integration**: FastAPI application deployment via git clone requires ansible.builtin.git module with proper change detection
- **Systemd Service Management**: Custom systemd service file creation and management requires ansible.builtin.systemd and template modules

### Migration Order

1. **cache** (low risk, foundational service) - Redis and memcached are standalone services with minimal dependencies
2. **nginx-multisite** (moderate complexity) - Web server configuration with security hardening, depends on SSL certificate strategy
3. **fastapi-tutorial** (high complexity) - Application deployment with database dependencies, requires coordination with cache services

### Assumptions

- SSL certificates are manually deployed or managed outside of Chef configuration (no certificate generation/renewal logic found in cookbooks)
- The target environment has internet access for package installation and git repository cloning
- PostgreSQL service installation and basic configuration is handled by system packages rather than custom compilation
- The Ruby-based Redis configuration patching is a workaround for cookbook limitations rather than a required business logic
- Static HTML files in nginx-multisite/files/ directory are simple placeholder content that can be deployed via Ansible copy module
- The Vagrant development environment will be replaced with an equivalent Ansible-based local testing setup
- UFW firewall rules are the primary firewall mechanism (no iptables or other firewall tools in use)
- The Chef Solo execution model suggests this is primarily for single-node deployments rather than multi-node orchestration