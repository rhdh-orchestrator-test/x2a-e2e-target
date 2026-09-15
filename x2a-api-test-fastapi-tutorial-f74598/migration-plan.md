# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing web services, caching infrastructure, and a FastAPI application. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to multi-service dependencies and security configurations. Estimated timeline: 3-4 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx reverse proxy with SSL-enabled multi-site hosting, security hardening via fail2ban/UFW, and self-signed certificate generation for development environments
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multiple SSL virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local), fail2ban intrusion prevention, UFW firewall configuration, SSH hardening, sysctl security tuning, self-signed certificate generation

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration management
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached service setup, Redis with password authentication, custom Redis configuration file manipulation, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database backend, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Python 3 virtual environment, Git repository cloning, PostgreSQL database and user creation, systemd service management, environment variable configuration

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run configuration with cookbook execution order and attribute overrides
- `solo.rb`: Chef Solo configuration file for local cookbook execution
- `Vagrantfile`: Development environment provisioning (requires migration consideration for testing)
- `vagrant-provision.sh`: Shell script for Vagrant environment setup

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be VM-based deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom Redis configuration tasks

### Security Considerations

- **SSH Hardening**: Root login disabled, password authentication disabled - migrate to ansible.posix.sshd_config module
- **Firewall Configuration**: UFW rules for SSH (22), HTTP (80), HTTPS (443) - migrate to community.general.ufw module
- **Intrusion Prevention**: fail2ban jail configuration for nginx - migrate to community.general.fail2ban module
- **SSL/TLS Certificates**: Self-signed certificate generation for development - migrate to community.crypto.openssl_* modules
- **Vault/secrets management**: 
  - Hardcoded credentials found in cache cookbook (Redis password: 'redis_secure_password_123')
  - PostgreSQL credentials in fastapi-tutorial cookbook (database password: 'fastapi_password')
  - SSL certificate generation with hardcoded subject information
  - Credentials are embedded directly in recipe files and need to be externalized to Ansible Vault

### Technical Challenges

- **Redis Configuration Manipulation**: The cache cookbook includes a Ruby block that manually edits Redis configuration files to remove specific directives - this will need custom Ansible tasks using lineinfile or template modules
- **Multi-Site SSL Management**: Dynamic SSL certificate generation and nginx site configuration based on attributes requires Ansible loops and conditional logic
- **Service Dependencies**: Proper ordering of PostgreSQL, Redis, memcached, and nginx services with their dependent applications
- **Template Migration**: Converting ERB templates (nginx.conf.erb, site.conf.erb, etc.) to Jinja2 format
- **Attribute Override Complexity**: The solo.json file overrides default attributes, requiring careful mapping to Ansible variables and group_vars

### Migration Order

1. **cache** (low risk, foundational service) - Redis and memcached setup with minimal external dependencies
2. **fastapi-tutorial** (moderate complexity) - Application deployment with database dependencies
3. **nginx-multisite** (high complexity) - Complex multi-site configuration with security hardening and SSL management

### Assumptions

- The target environment will maintain the same OS support (Ubuntu 18.04+, CentOS 7+) as specified in cookbook metadata
- Self-signed certificates are acceptable for development environments (production would require Let's Encrypt or CA-signed certificates)
- The Vagrant development workflow will be replaced with molecule testing or similar Ansible testing framework
- Current hardcoded passwords are acceptable for development but will need proper secret management for production
- The three-site configuration (test.cluster.local, ci.cluster.local, status.cluster.local) represents the standard deployment pattern
- PostgreSQL and Redis services will continue to run on the same host as the applications (no containerization or service separation planned)
- The Chef Solo execution model will be replaced with Ansible playbook execution, maintaining the same run order
- UFW firewall rules are sufficient and no migration to iptables or other firewall solutions is required