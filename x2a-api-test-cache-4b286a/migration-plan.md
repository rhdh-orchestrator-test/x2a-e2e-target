# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing web services, caching, and application deployment. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to external dependencies and security configurations. Estimated timeline: 3-4 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with SSL-enabled multi-site hosting, security hardening via fail2ban/UFW, and system-level security configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multiple SSL virtual hosts (test/ci/status subdomains), fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security parameters

- **cache**:
    - Description: Caching services layer providing both Memcached and Redis with authentication and custom configuration management
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, custom log directory setup, configuration file patching via ruby_block, Memcached integration

- **fastapi-tutorial**:
    - Description: FastAPI Python web application with PostgreSQL database backend, systemd service management, and virtual environment setup
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository cloning, Python virtual environment, PostgreSQL database/user creation, systemd service configuration, environment variable management

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list and node attributes configuration with site definitions and security settings
- `solo.rb`: Chef Solo configuration file for local cookbook execution
- `Vagrantfile`: Development environment provisioning (requires review for Ansible conversion)
- `vagrant-provision.sh`: Shell provisioning script for development setup

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant-based development environment (VirtualBox/VMware inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service management via systemd
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom configuration templates

### Security Considerations

- **Hardcoded Credentials**: Multiple plaintext passwords found requiring Ansible Vault migration:
  - Redis password: 'redis_secure_password_123' in cache cookbook
  - PostgreSQL password: 'fastapi_password' in fastapi-tutorial cookbook
  - Database connection strings with embedded credentials in .env files
- **SSL Certificate Management**: SSL certificate paths configured but certificate provisioning method unclear - requires investigation of certificate deployment strategy
- **SSH Hardening**: Root login disabled, password authentication disabled - migrate to ansible.posix.sshd_config module
- **Firewall Configuration**: UFW rules for HTTP/HTTPS/SSH - migrate to community.general.ufw module
- **Fail2ban Integration**: Custom jail configuration for nginx protection - migrate to community.general.fail2ban module

### Technical Challenges

- **Ruby Block Workarounds**: Cache cookbook contains ruby_block hack for Redis configuration file manipulation - requires conversion to Ansible lineinfile or template modules with proper logic
- **Service Dependencies**: Complex service startup ordering (PostgreSQL before FastAPI, nginx after SSL setup) - implement with Ansible handlers and proper task dependencies
- **Multi-site Configuration**: Dynamic site generation from attributes requires Jinja2 templating and loop structures in Ansible
- **Git Repository Management**: FastAPI cookbook clones from GitHub - migrate to ansible.builtin.git module with proper idempotency checks
- **Virtual Environment Management**: Python venv creation and pip installations require ansible.builtin.pip module with virtualenv parameters

### Migration Order

1. **cache** (low risk, foundational service) - Redis and Memcached setup with minimal external dependencies
2. **nginx-multisite** (moderate complexity) - Web server with security configurations, depends on SSL certificate strategy
3. **fastapi-tutorial** (high complexity) - Application deployment with database dependencies and service management

### Assumptions

- SSL certificates are manually deployed or managed externally (no certificate generation logic found in cookbooks)
- Development environment uses Vagrant but production deployment method is unspecified
- External cookbook dependencies (nginx, memcached, redisio) provide standard functionality that can be replaced with native Ansible modules
- Current Chef Solo execution model suggests single-node deployments rather than multi-node orchestration
- PostgreSQL installation assumes default package repository versions are acceptable
- Git repository access (https://github.com/dibanez/fastapi_tutorial.git) remains available and accessible from target systems
- System package managers (apt/yum) are available and configured on target systems
- Target systems have internet connectivity for package installation and git cloning operations