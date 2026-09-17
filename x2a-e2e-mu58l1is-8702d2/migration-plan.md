# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with nginx reverse proxy, caching services (Redis/Memcached), and a FastAPI Python application with PostgreSQL backend. The migration involves 3 custom cookbooks with moderate complexity, requiring approximately 4-6 weeks for complete migration including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **cache**:
    - Description: Caching services configuration with Redis authentication and Memcached setup, includes Redis log directory management and configuration file patching
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached integration, custom Redis config file manipulation, log directory setup

- **fastapi-tutorial**:
    - Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository cloning, Python virtual environment, PostgreSQL database and user creation, systemd service management, environment configuration

- **nginx-multisite**:
    - Description: Nginx reverse proxy with SSL-enabled multi-site configuration, security hardening, and self-signed certificate generation
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multiple SSL virtual hosts, fail2ban integration, UFW firewall configuration, SSH hardening, self-signed certificate generation, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list configuration and node attributes for site definitions and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning configuration
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox (based on Vagrantfile presence)
- **Cloud Platform**: Not specified (local development environment focus)

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis or custom Redis configuration tasks

### Security Considerations

- **Hardcoded Credentials**: Redis password 'redis_secure_password_123' and PostgreSQL password 'fastapi_password' are hardcoded in recipes - migrate to Ansible Vault
- **SSL Certificate Management**: Self-signed certificates generated via OpenSSL commands - consider Let's Encrypt integration or proper certificate management
- **SSH Security Configuration**: Root login disabled, password authentication disabled - maintain these security practices in Ansible
- **Firewall Configuration**: UFW rules for SSH, HTTP, HTTPS - migrate to ansible.posix.ufw module
- **Fail2ban Integration**: Jail configuration for nginx protection - migrate to community.general.fail2ban
- **Sysctl Security Tuning**: Kernel parameter hardening - migrate to ansible.posix.sysctl module

### Technical Challenges

- **Redis Configuration Patching**: The cache cookbook includes a Ruby block that manually edits Redis config files to remove specific directives - this complex logic needs careful translation to Ansible lineinfile or template modules
- **Multi-site SSL Management**: Dynamic SSL certificate generation and nginx site configuration for multiple domains requires Ansible loops and conditional logic
- **Service Dependencies**: PostgreSQL must be running before database creation, nginx must reload after configuration changes - ensure proper task ordering and handlers
- **File Permissions and Ownership**: Complex SSL certificate permissions (ssl-cert group) and web directory ownership need careful mapping to Ansible file modules
- **Git Repository Management**: FastAPI application deployment from Git requires idempotent repository management

### Migration Order

1. **cache cookbook** (moderate complexity, foundational service)
2. **fastapi-tutorial cookbook** (moderate complexity, application layer)
3. **nginx-multisite cookbook** (high complexity, depends on application services)

### Assumptions

- Target systems will maintain Ubuntu/CentOS compatibility as specified in cookbook metadata
- Current hardcoded passwords are acceptable for development environments but should be vaulted for production
- Self-signed certificates are sufficient for the current use case (no Let's Encrypt requirement specified)
- The Ruby-based Redis configuration patching indicates potential compatibility issues that may need investigation
- Vagrant-based development workflow will be maintained or replaced with equivalent Ansible testing approach
- External cookbook dependencies (nginx, memcached, redisio) functionality can be replicated with native Ansible modules
- The multi-site nginx configuration pattern suggests a template-driven approach will be needed in Ansible
- PostgreSQL database and user creation assumes local database installation rather than external database service