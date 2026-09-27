# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages web services, caching layers, and a FastAPI application with comprehensive security hardening. The migration involves 3 cookbooks with moderate complexity, requiring approximately 4-6 weeks for a complete migration including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx reverse proxy with SSL-enabled multi-site hosting, security hardening via fail2ban/UFW, and sysctl kernel parameter tuning
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multiple SSL virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local), fail2ban intrusion prevention, UFW firewall configuration, SSH hardening, kernel security parameters

**cache**:
- Description: Dual caching service configuration with memcached and Redis, including authentication and custom Redis configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication, memcached service, custom Redis configuration patching via ruby_block, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database backend, systemd service management, and virtual environment isolation
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment, PostgreSQL database and user creation, systemd service configuration, environment variable management

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list configuration and node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file
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

- **SSH Hardening**: Root login disabled, password authentication disabled - migrate to ansible.posix.sysctl and ansible.builtin.lineinfile modules
- **Firewall Configuration**: UFW rules for SSH (22), HTTP (80), HTTPS (443) - migrate to community.general.ufw module
- **Intrusion Prevention**: fail2ban jail configuration - migrate to community.general.ini_file module
- **Kernel Security**: sysctl parameters via template - migrate to ansible.posix.sysctl module
- **Vault/secrets management**: 
  - Redis password hardcoded in recipe (redis_secure_password_123)
  - PostgreSQL password hardcoded in recipe (fastapi_password)
  - Database credentials in .env file
  - SSL certificate paths configured but certificates not managed in code
  - Recommend migrating to Ansible Vault for all credential management

### Technical Challenges

- **Ruby Block Logic**: The cache cookbook uses a ruby_block to patch Redis configuration files post-installation, requiring custom Ansible tasks with ansible.builtin.replace or ansible.builtin.lineinfile modules
- **Git Repository Management**: FastAPI cookbook clones from GitHub - ensure network access and consider using ansible.builtin.git module with proper SSH key management
- **Service Dependencies**: PostgreSQL must be running before database user creation - use Ansible handlers and proper task ordering
- **Template Migration**: Convert ERB templates (nginx.conf.erb, security.conf.erb, etc.) to Jinja2 format
- **Multi-site Configuration**: Dynamic site creation based on node attributes requires Ansible loops and conditional logic

### Migration Order

1. **cache** (low risk, standalone service, clear dependencies)
2. **nginx-multisite** (moderate complexity, security configurations, template conversion needed)
3. **fastapi-tutorial** (highest complexity, database dependencies, application deployment, systemd service management)

### Assumptions

- SSL certificates are managed externally and placed in /etc/ssl/certs and /etc/ssl/private directories
- The FastAPI tutorial repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and stable
- Target systems have internet access for package installation and git repository cloning
- PostgreSQL service can be managed via system package manager (not containerized)
- Current Chef Solo deployment model will be replaced with Ansible playbook execution
- Development environment (Vagrant) configuration is not part of the production migration scope
- The ruby_block configuration fixes in the cache cookbook are still necessary for the target Redis version
- Site-specific HTML files (ci/index.html, status/index.html, test/index.html) will be migrated as static files
- UFW firewall rules are appropriate for the target environment and no additional ports need to be opened