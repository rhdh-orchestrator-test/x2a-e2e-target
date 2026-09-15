# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing caching services, a FastAPI application, and a multi-site nginx web server with SSL and security hardening. The migration involves converting Chef cookbooks to Ansible playbooks and roles, addressing external dependencies, and maintaining security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached installation, Redis with password authentication (redis_secure_password_123), custom Redis configuration patching via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment setup, and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment, PostgreSQL database and user creation, systemd service configuration, environment file with database credentials

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening via fail2ban and UFW firewall, and SSH configuration
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration with self-signed certificates, fail2ban intrusion prevention, UFW firewall rules, SSH hardening (root login disabled, password auth disabled), sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo configuration with run list and node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file for cookbook paths and execution settings
- `Vagrantfile`: Development environment provisioning for testing cookbook functionality
- `vagrant-provision.sh`: Shell script for Vagrant VM provisioning and Chef Solo execution

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or VM-based deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx configuration
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules for memcached installation and management
- **redisio (~> 7.2.4)**: Replace with ansible.builtin.package, ansible.builtin.template for redis.conf, and ansible.builtin.service modules for Redis configuration

### Security Considerations

- **Hardcoded Credentials**: Redis password (redis_secure_password_123) and PostgreSQL credentials (fastapi:fastapi_password) are embedded in recipe code - migrate to Ansible Vault
- **SSL Certificate Management**: Self-signed certificate generation via OpenSSL commands - consider using ansible.builtin.openssl_* modules or community.crypto collection
- **SSH Hardening**: Root login disabled and password authentication disabled via sed commands - migrate to ansible.builtin.lineinfile module
- **Firewall Configuration**: UFW rules for SSH, HTTP, HTTPS - migrate to community.general.ufw module
- **Fail2ban Configuration**: Intrusion prevention with custom jail.local template - migrate to ansible.builtin.template module
- **Credential Types per Module**:
  - cache: Redis authentication password (hardcoded)
  - fastapi-tutorial: PostgreSQL database credentials (hardcoded), application environment variables
  - nginx-multisite: SSL certificate generation (self-signed), no external credentials

### Technical Challenges

- **Ruby Block Logic**: The cache cookbook contains a ruby_block that performs complex Redis configuration file manipulation - will need to be replaced with ansible.builtin.lineinfile or ansible.builtin.replace modules with multiple tasks
- **Git Repository Cloning**: FastAPI tutorial clones from GitHub - ensure network connectivity and consider using ansible.builtin.git module with proper error handling
- **Service Dependencies**: PostgreSQL must be running before database creation, nginx must reload after configuration changes - use Ansible handlers and task dependencies
- **Multi-Site SSL**: Dynamic SSL certificate generation for multiple sites requires loop constructs in Ansible with proper certificate validation
- **Cross-Platform Support**: Cookbooks support both Ubuntu and CentOS - ensure Ansible playbooks handle package manager differences (apt vs yum)

### Migration Order

1. **cache** (low risk, high value) - Simple service installation with well-defined dependencies, good starting point for team familiarity
2. **fastapi-tutorial** (moderate complexity) - Application deployment with database dependencies, moderate complexity for learning Ansible patterns
3. **nginx-multisite** (high complexity, dependencies) - Complex multi-site configuration with security hardening, SSL management, and firewall rules

### Assumptions

- Current Chef cookbooks are functional and represent the desired end state for Ansible migration
- External cookbook dependencies (nginx, memcached, redisio) from Chef Supermarket will be replaced with native Ansible modules rather than community roles
- Self-signed SSL certificates are acceptable for the target environment (no Let's Encrypt or CA-signed certificate requirements identified)
- PostgreSQL and Redis services will continue to run on the same hosts as the applications (no separation to dedicated database servers)
- The target environment has internet connectivity for package installation and git repository cloning
- UFW firewall and fail2ban are the preferred security tools (no requirement to migrate to different security solutions)
- Systemd is available on target systems for service management (Ubuntu 18.04+ and CentOS 7+ support confirmed)
- The migration will maintain the same multi-platform support (Ubuntu and CentOS) as the original Chef cookbooks