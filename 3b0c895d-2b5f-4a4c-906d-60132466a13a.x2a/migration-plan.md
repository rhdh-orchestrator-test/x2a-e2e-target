# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing web services, caching infrastructure, and a Python FastAPI application. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to security configurations, SSL certificate management, and database setup. Estimated timeline: 3-4 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication, custom log directory setup, and configuration file patching
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis password authentication (redis_secure_password_123), memcached integration, Redis log directory management, configuration file manipulation via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment setup, and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment creation, PostgreSQL database and user provisioning, systemd service configuration, environment file management

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening via fail2ban and UFW firewall, and self-signed certificate generation
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site configuration (test.cluster.local, ci.cluster.local, status.cluster.local), SSL certificate generation, fail2ban integration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef cookbook dependency management with external dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo configuration with run list and node attributes for site configurations and security settings
- `solo.rb`: Chef Solo execution configuration
- `Vagrantfile`: Development environment provisioning (requires review for Ansible equivalent)
- `vagrant-provision.sh`: Shell provisioning script for Vagrant integration

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be local development environment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom Redis configuration tasks

### Security Considerations

- **Hardcoded Credentials**: Redis password 'redis_secure_password_123' and PostgreSQL password 'fastapi_password' are hardcoded in recipes - migrate to Ansible Vault
- **SSL Certificate Management**: Self-signed certificate generation for development environments - consider Let's Encrypt integration for production
- **SSH Hardening**: Root login disabled, password authentication disabled - preserve these security configurations
- **Firewall Configuration**: UFW rules for HTTP/HTTPS/SSH - migrate to ansible.posix.ufw module
- **Fail2ban Integration**: SSH protection via fail2ban - migrate to community.general.fail2ban module
- **Sysctl Security Tuning**: Kernel parameter hardening via sysctl - migrate to ansible.posix.sysctl module
- **Credential Types per Module**:
  - cache: Redis authentication password (plaintext in attributes)
  - fastapi-tutorial: PostgreSQL database credentials (plaintext in recipe)
  - nginx-multisite: SSL certificate generation (self-signed, no stored credentials)

### Technical Challenges

- **Ruby Block Logic**: The cache cookbook uses a ruby_block to manipulate Redis configuration files post-installation - requires conversion to Ansible lineinfile or template modules
- **Complex Site Configuration**: nginx-multisite cookbook dynamically generates site configurations based on node attributes - requires Jinja2 templating and loop structures
- **Service Dependencies**: FastAPI service depends on PostgreSQL being ready - requires proper Ansible handler ordering and dependency management
- **File Permissions**: SSL certificate files have specific ownership (root:ssl-cert) and permissions (640/710) - requires careful attention to file module parameters
- **Conditional Logic**: Security configurations have conditional execution based on node attributes - requires Ansible when conditions

### Migration Order

1. **cache** (low risk, standalone service) - Redis and memcached are independent services with minimal external dependencies
2. **nginx-multisite** (moderate complexity) - Web server configuration with security hardening, but no application dependencies
3. **fastapi-tutorial** (high complexity) - Application deployment with database dependencies, requires coordination with other services

### Assumptions

- Target environments will maintain Ubuntu/CentOS compatibility as specified in cookbook metadata
- Self-signed certificates are acceptable for development environments (production may require Let's Encrypt or corporate CA integration)
- Current hardcoded passwords are development-only and will be replaced with proper secret management
- Vagrant development workflow will be preserved or replaced with equivalent Ansible-based local development setup
- PostgreSQL and Redis services will continue to run on the same hosts as the applications (no migration to external managed services)
- The three-site configuration (test.cluster.local, ci.cluster.local, status.cluster.local) represents the complete scope of required sites
- UFW firewall rules are sufficient for the security requirements (no need for iptables or other firewall solutions)
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) will remain accessible and the 'main' branch will be stable
- Current Chef Solo execution model will be replaced with Ansible playbook execution (no Chef Server migration required)