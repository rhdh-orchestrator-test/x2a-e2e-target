# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with 3 cookbooks managing web services, caching infrastructure, and a FastAPI application. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to security configurations, SSL management, and database setup. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including authentication, log directory setup, and configuration file patching
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis authentication with hardcoded password, memcached integration, custom Redis configuration patching via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python application deployment with PostgreSQL database, virtual environment setup, and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python venv creation, PostgreSQL database and user provisioning, systemd service configuration, environment file with database credentials

**nginx-multisite**:
- Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and fail2ban protection
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-domain SSL configuration, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security parameters

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx, memcached, redisio) and local cookbook references
- `solo.json`: Chef Solo run configuration with run_list and node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file for cookbook and data bag paths
- `Vagrantfile`: Development environment provisioning with Chef Solo integration
- `vagrant-provision.sh`: Bootstrap script for Vagrant environment setup

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support specified in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or cloud-agnostic deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom configuration tasks
- **Chef Solo**: Replace with Ansible playbook execution via ansible-playbook command

### Security Considerations

- **Hardcoded Credentials**: Redis password ('redis_secure_password_123') and PostgreSQL credentials ('fastapi_password') are embedded in recipes - migrate to Ansible Vault
- **SSL Certificate Management**: SSL certificate paths configured but certificate provisioning not automated - implement certificate deployment strategy
- **SSH Hardening**: Root login disabled, password authentication disabled - preserve these security configurations
- **Firewall Configuration**: UFW rules for HTTP/HTTPS/SSH - maintain equivalent iptables or firewalld rules
- **Fail2ban Integration**: Jail configuration for nginx protection - preserve fail2ban rules and templates
- **Sysctl Security Parameters**: Kernel security hardening via sysctl - maintain security.conf template content

### Technical Challenges

- **Ruby Block Logic**: Custom Redis configuration patching using ruby_block needs conversion to Ansible lineinfile or replace modules
- **Chef Resource Notifications**: Delayed notifications for service restarts need conversion to Ansible handlers
- **Template Dependencies**: ERB templates (.erb files) need conversion to Jinja2 (.j2) format
- **Attribute Precedence**: Chef attribute precedence (default, override) needs mapping to Ansible variable precedence
- **Git Repository Management**: Chef git resource behavior needs replication with ansible.builtin.git module
- **PostgreSQL User Management**: Chef execute blocks for database setup need conversion to community.postgresql.* modules

### Migration Order

1. **cache** (low risk, standalone caching services with clear dependencies)
2. **nginx-multisite** (moderate complexity, security configurations require careful testing)
3. **fastapi-tutorial** (high complexity, database dependencies and application deployment)

### Assumptions

- SSL certificates will be provided externally or generated via Let's Encrypt integration (not currently automated in Chef)
- PostgreSQL installation and initial configuration is handled by system packages (not a dedicated database cookbook)
- The 'redisio' cookbook configuration can be replicated using standard Redis configuration files
- UFW firewall rules are sufficient for the target environment (no complex iptables requirements)
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and compatible
- Development environment will continue using Vagrant or migrate to alternative local development solution
- Current Chef Solo execution model can be replaced with standard Ansible playbook execution
- The ruby_block configuration patching for Redis can be replaced with more maintainable configuration file management