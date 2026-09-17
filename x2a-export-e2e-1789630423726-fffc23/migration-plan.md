# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing web services, caching infrastructure, and a FastAPI application. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to security configurations, SSL management, and database setup. Estimated timeline: 3-4 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including authentication and custom Redis configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication, memcached integration, custom Redis config patching, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python application deployment with PostgreSQL database, virtual environment setup, and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment, PostgreSQL database and user creation, systemd service configuration, environment file management

**nginx-multisite**:
- Description: Nginx web server with multiple SSL-enabled subdomains, security hardening, and fail2ban protection
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, fail2ban integration, UFW firewall rules, SSH hardening, sysctl security tuning, custom nginx configuration templates

### Infrastructure Files

- `Berksfile`: Chef cookbook dependency management - migrate to Ansible Galaxy requirements.yml
- `solo.json`: Chef node configuration with run_list and attributes - convert to Ansible inventory and group_vars
- `solo.rb`: Chef Solo configuration - replace with ansible.cfg
- `Vagrantfile`: Development environment provisioning - update to use Ansible provisioner
- `vagrant-provision.sh`: Shell provisioning script - integrate into Ansible playbooks

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox (based on Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be local/on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **memcached (~> 6.0)**: Replace with ansible.builtin.package and community.general.memcached modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis and ansible.builtin.template for configuration
- **nginx (~> 12.0)**: Replace with community.general.nginx and ansible.builtin.template modules

### Security Considerations

- **Hardcoded credentials**: Redis password and PostgreSQL credentials are embedded in recipes - migrate to Ansible Vault
- **SSL certificate management**: SSL paths and configuration need secure handling in Ansible
- **SSH hardening**: Root login disable and password authentication disable configurations
- **Firewall rules**: UFW configuration with specific port allowances (SSH, HTTP, HTTPS)
- **Fail2ban configuration**: Intrusion prevention system setup with custom jail configurations
- **Sysctl security tuning**: Kernel parameter hardening via template-driven configuration

Credential patterns identified:
- Redis: Hardcoded password 'redis_secure_password_123' in cache cookbook
- PostgreSQL: Hardcoded credentials 'fastapi:fastapi_password' in fastapi-tutorial cookbook
- SSL certificates: File path references without credential management

### Technical Challenges

- **Redis configuration patching**: The cache cookbook includes a Ruby block that manually edits Redis config files to remove specific directives - this will need to be reimplemented using Ansible's lineinfile or template modules
- **Multi-site SSL management**: The nginx-multisite cookbook manages multiple SSL-enabled sites with dynamic configuration - requires careful template conversion and certificate deployment strategy
- **Database initialization**: PostgreSQL user and database creation with proper privilege management needs conversion from shell commands to Ansible postgresql modules
- **Service dependencies**: Complex service restart notifications and dependency chains between nginx, fail2ban, and SSH services
- **Template conversion**: Multiple ERB templates need conversion to Jinja2 format (nginx.conf, security.conf, site.conf, fail2ban.jail.local, sysctl-security.conf)

### Migration Order

1. **cache** (low risk, isolated functionality) - Redis and memcached services with minimal external dependencies
2. **nginx-multisite** (moderate complexity) - Web server with security configurations, depends on SSL certificate availability
3. **fastapi-tutorial** (high complexity) - Application deployment with database dependencies, requires coordination with nginx for reverse proxy setup

### Assumptions

- SSL certificates are manually managed and available at specified paths (/etc/ssl/certs, /etc/ssl/private)
- PostgreSQL service is expected to be available on the target system or will be installed as part of the migration
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and compatible
- Current Chef Solo deployment model will be replaced with Ansible playbook execution
- UFW firewall is the preferred firewall solution for the target environment
- Systemd is available on target systems for service management
- The three configured sites (test.cluster.local, ci.cluster.local, status.cluster.local) represent the complete multi-site configuration requirements
- Redis configuration patching workaround in the cache cookbook indicates compatibility issues that may need addressing in the Ansible version
- No external Chef Supermarket cookbooks beyond those listed in Berksfile are required for functionality