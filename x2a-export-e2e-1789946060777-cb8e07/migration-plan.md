# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing caching services, a FastAPI application, and a multi-site nginx reverse proxy with SSL termination. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to security configurations, SSL certificate management, and database setup. Estimated timeline: 3-4 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached installation, Redis with password authentication (redis_secure_password_123), custom Redis configuration patching, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database backend, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Python 3 virtual environment, Git repository cloning, PostgreSQL database and user creation, systemd service management, environment configuration file

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening via fail2ban and UFW firewall, and self-signed certificate generation
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site nginx configuration, SSL certificate generation, fail2ban intrusion prevention, UFW firewall rules, SSH security hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef cookbook dependency management - defines external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo configuration with run list and node attributes - contains site configurations and security settings
- `solo.rb`: Chef Solo execution configuration
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be VM-based deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks

### Security Considerations

- **Hardcoded Credentials**: Redis password (redis_secure_password_123) and PostgreSQL credentials (fastapi:fastapi_password) are hardcoded in recipes - migrate to Ansible Vault
- **SSL Certificate Management**: Self-signed certificate generation for development environments - consider using community.crypto.openssl_* modules
- **SSH Security Configuration**: Root login disabled, password authentication disabled - migrate using ansible.posix.sysctl and lineinfile modules
- **Firewall Rules**: UFW configuration for HTTP/HTTPS/SSH access - migrate using community.general.ufw module
- **Fail2ban Configuration**: Intrusion prevention system - migrate using ansible.builtin.template and service modules
- **Database Credentials**: PostgreSQL user and database creation with embedded passwords - migrate to Ansible Vault for credential management

### Technical Challenges

- **Redis Configuration Patching**: The cache cookbook includes a Ruby block that manually edits Redis configuration files to remove specific directives - this will need to be reimplemented using Ansible's lineinfile or replace modules with appropriate regex patterns
- **Multi-site SSL Certificate Generation**: Each nginx site requires individual SSL certificate generation with site-specific parameters - will need to implement with loops and conditional logic in Ansible
- **Service Dependencies**: FastAPI service depends on PostgreSQL being available - ensure proper task ordering and handlers in Ansible playbooks
- **Template Migration**: Chef ERB templates need conversion to Jinja2 format, particularly nginx.conf.erb, security.conf.erb, and fail2ban.jail.local.erb

### Migration Order

1. **cache** (low risk, standalone service) - Start with caching services as they have minimal dependencies and clear configuration patterns
2. **nginx-multisite** (moderate complexity) - Security configurations and SSL management require careful testing but are well-defined
3. **fastapi-tutorial** (high complexity, database dependencies) - Application deployment with database setup and service management should be migrated last due to interdependencies

### Assumptions

- The target environment will continue to use Ubuntu/CentOS as specified in cookbook metadata
- Self-signed certificates are acceptable for development environments (production may require Let's Encrypt or CA-signed certificates)
- Current hardcoded passwords are acceptable for development but will need proper secret management for production
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and compatible
- PostgreSQL will continue to be used as the database backend for the FastAPI application
- The three-site configuration (test.cluster.local, ci.cluster.local, status.cluster.local) represents the complete scope of nginx sites
- UFW firewall rules are sufficient for the security requirements (no additional iptables rules needed)
- The Redis configuration patching in the cache cookbook addresses specific compatibility issues that will still be relevant in the Ansible implementation