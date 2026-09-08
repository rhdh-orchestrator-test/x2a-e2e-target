# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing web services, caching, and a FastAPI application. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to security configurations, SSL management, and database setup. Estimated timeline: 3-4 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx reverse proxy with SSL-enabled multi-site hosting, security hardening via fail2ban/UFW, and system-level security configurations
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multiple SSL virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local), fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security parameters

**cache**:
- Description: Caching services configuration with memcached and Redis, including authentication and custom Redis configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication, memcached service, custom Redis configuration patching via ruby_block, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python application deployment with PostgreSQL database, virtual environment setup, and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment, PostgreSQL database and user creation, systemd service configuration, environment variable management

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list and node attributes configuration with site definitions and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox (based on Vagrantfile presence)
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address
- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom configuration templates

### Security Considerations
- SSH hardening configurations: Migrate PermitRootLogin and PasswordAuthentication settings using ansible.posix.sshd_config
- Firewall management: Convert UFW commands to community.general.ufw module calls
- Fail2ban configuration: Migrate jail.local template to Ansible template module
- SSL certificate management: Handle certificate and private key deployment securely
- Credential patterns identified:
  - Redis password hardcoded in attributes: 'redis_secure_password_123'
  - PostgreSQL credentials hardcoded: 'fastapi_password'
  - Database connection strings in environment files
  - SSL certificate paths in configuration

### Technical Challenges
- **Ruby block configuration fixes**: The cache cookbook uses a ruby_block to patch Redis configuration files post-installation. This will need to be converted to Ansible lineinfile or replace modules with appropriate regex patterns.
- **Git repository management**: FastAPI cookbook clones from GitHub - ensure Ansible git module handles repository updates and authentication properly.
- **Service dependencies**: PostgreSQL must be running before database user creation. Ensure proper task ordering with handlers and dependencies.
- **Template variable mapping**: Chef ERB templates need conversion to Jinja2 with attribute-to-variable mapping.
- **Multi-site SSL configuration**: Complex nginx virtual host configuration with SSL requires careful template migration and certificate management.

### Migration Order
1. **cache** (low risk, minimal dependencies, good starting point)
2. **fastapi-tutorial** (moderate complexity, database setup, systemd service)
3. **nginx-multisite** (high complexity, security configurations, SSL management, multiple interdependent recipes)

### Assumptions
- SSL certificates are manually managed and placed in /etc/ssl/certs and /etc/ssl/private directories
- The FastAPI tutorial repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and the main branch is stable
- PostgreSQL service configuration beyond basic installation is handled externally
- The ruby_block Redis configuration fix addresses specific version compatibility issues that may not apply to newer Redis versions
- UFW and fail2ban packages are available in target system repositories
- The target environment has internet access for package installation and git repository cloning
- Systemd is the service manager on target systems
- The nginx external cookbook dependency provides standard nginx installation and basic configuration
- Site-specific HTML files (ci/index.html, status/index.html, test/index.html) are static and don't require dynamic generation