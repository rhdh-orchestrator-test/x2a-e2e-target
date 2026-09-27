# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing caching services, a FastAPI application, and an nginx multi-site reverse proxy with SSL termination. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to external dependencies and security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

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
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening, and fail2ban protection
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, self-signed certificate generation, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list and node attributes configuration with site definitions and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox (based on Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be local/on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom Redis configuration tasks

### Security Considerations

- **Hardcoded Credentials**: Redis password (redis_secure_password_123) and PostgreSQL credentials (fastapi:fastapi_password) are hardcoded in recipes - migrate to Ansible Vault
- **SSL Certificate Management**: Self-signed certificates generated via OpenSSL commands - consider Let's Encrypt integration or proper certificate management
- **SSH Hardening**: Root login disabled, password authentication disabled - preserve in Ansible with ansible.posix.sshd_config module
- **Firewall Configuration**: UFW rules for SSH, HTTP, HTTPS - migrate to community.general.ufw module
- **Fail2ban Configuration**: Custom jail.local template - migrate to community.general.fail2ban module
- **Credential Types per Module**:
  - cache: Redis authentication password
  - fastapi-tutorial: PostgreSQL database credentials, application environment variables
  - nginx-multisite: SSL certificate generation, no stored credentials but certificate management

### Technical Challenges

- **Redis Configuration Patching**: The cache cookbook includes a Ruby block that manually edits Redis configuration files to remove specific directives - this will need to be reimplemented using Ansible's lineinfile or template modules
- **Complex Service Dependencies**: FastAPI service depends on PostgreSQL being ready, and nginx depends on SSL certificates being generated - ensure proper task ordering and handlers in Ansible
- **Multi-site SSL Management**: Dynamic SSL certificate generation for multiple sites based on node attributes - implement with Ansible loops and conditional certificate generation
- **Template Migration**: Convert ERB templates (nginx.conf.erb, security.conf.erb, site.conf.erb) to Jinja2 format for Ansible

### Migration Order

1. **cache** (low risk, standalone service with clear dependencies)
2. **nginx-multisite** (moderate complexity, security configurations but well-defined scope)
3. **fastapi-tutorial** (highest complexity due to application deployment, database setup, and service management)

### Assumptions

- The target environment will maintain the same OS support (Ubuntu 18.04+, CentOS 7+) as specified in cookbook metadata
- Self-signed certificates are acceptable for the target environment, or proper CA-signed certificates will be provided separately
- The Redis configuration patching hack in the cache cookbook is still necessary in the target environment
- PostgreSQL and Redis services will continue to run on the same hosts as the applications
- The three-site configuration (test.cluster.local, ci.cluster.local, status.cluster.local) represents the complete scope of required sites
- Vagrant-based development workflow will be replaced with molecule or similar Ansible testing framework
- External cookbook dependencies (nginx, memcached, redisio) functionality can be replicated with native Ansible modules and community collections