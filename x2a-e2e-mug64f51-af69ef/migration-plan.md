# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with 3 cookbooks managing web services, caching, and application deployment. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to external dependencies and security configurations. Estimated timeline: 3-4 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx reverse proxy with SSL-enabled multi-site hosting, security hardening via fail2ban/UFW, and system-level security configurations
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multiple SSL virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local), fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security parameters

**cache**:
- Description: Dual caching service configuration with memcached and Redis, including authentication and custom Redis configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached service, Redis with password authentication (redis_secure_password_123), custom Redis configuration patching via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service management, environment variable configuration

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
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks

### Security Considerations
- SSH hardening configurations: Root login disabled, password authentication disabled
- Firewall management: UFW rules for SSH (22), HTTP (80), HTTPS (443) with default deny policy
- Intrusion detection: fail2ban jail configuration for nginx protection
- System hardening: sysctl security parameters via /etc/sysctl.d/99-security.conf
- Vault/secrets management: 
  - Redis password hardcoded in cache cookbook (redis_secure_password_123)
  - PostgreSQL credentials hardcoded in fastapi-tutorial cookbook (fastapi_password)
  - SSL certificate paths referenced but certificates not managed in code
  - Database connection strings with embedded credentials in .env files

### Technical Challenges
- **Custom Redis Configuration Patching**: The cache cookbook uses a ruby_block to manually edit Redis configuration files, removing specific directives. This will need to be replaced with Ansible template or lineinfile modules.
- **Git Repository Management**: FastAPI tutorial clones from external GitHub repository, requiring proper Git module configuration and credential handling in Ansible.
- **Service Dependencies**: Complex service startup order (PostgreSQL before FastAPI, nginx after SSL configuration) needs careful Ansible handler and dependency management.
- **Template Migration**: Multiple ERB templates (nginx.conf, security.conf, site.conf, fail2ban.jail.local, sysctl-security.conf) need conversion to Jinja2 format.

### Migration Order
1. **cache** (low risk, standalone service with clear dependencies)
2. **nginx-multisite** (moderate complexity, security configurations require careful testing)
3. **fastapi-tutorial** (high complexity, external dependencies and database integration)

### Assumptions
- SSL certificates are managed externally and will be available at the specified paths (/etc/ssl/certs, /etc/ssl/private)
- The FastAPI tutorial GitHub repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and the main branch is stable
- PostgreSQL service is expected to be managed by the system package manager rather than a dedicated database cookbook
- The target environment has internet access for package installation and Git repository cloning
- UFW firewall rules are appropriate for the target environment and won't conflict with existing network policies
- The custom Redis configuration fixes in the ruby_block are still necessary in the target environment
- Static HTML files for the nginx sites (ci/index.html, status/index.html, test/index.html) serve the same purpose in the migrated environment