# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with 3 cookbooks managing web services, caching infrastructure, and a Python application stack. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to external dependencies and security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx web server with multi-site SSL configuration, security hardening (fail2ban, UFW firewall), and SSH security controls
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: SSL-enabled virtual hosts for test/ci/status subdomains, fail2ban intrusion prevention, UFW firewall rules, SSH hardening (root login disabled, password auth disabled), sysctl security tuning

**cache**:
- Description: Caching services configuration providing both Memcached and Redis with authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached service, Redis with password authentication (requirepass), custom Redis configuration cleanup via ruby_block, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database backend, systemd service management, and virtual environment setup
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment, PostgreSQL database and user creation, systemd service configuration, environment file management

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbook dependencies (memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list and node attributes defining site configurations and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning (likely for testing)
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox (based on Vagrantfile presence for development)
- **Cloud Platform**: Not specified - appears to be VM-based deployment

## Migration Approach

### Key Dependencies to Address

- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis or custom Redis configuration tasks
- **nginx (~> 12.0)**: Replace with nginxinc.nginx_core collection or ansible.builtin.package with custom configuration

### Security Considerations

- **SSH Hardening**: Root login disabled, password authentication disabled - migrate to ansible.posix.sshd_config module
- **Firewall Management**: UFW firewall rules for HTTP/HTTPS/SSH - migrate to community.general.ufw module
- **Intrusion Prevention**: fail2ban configuration with custom jail.local - migrate to community.general.ini_file or template module
- **System Hardening**: sysctl security parameters via template - migrate to ansible.posix.sysctl module
- **Vault/secrets management**: 
  - Hardcoded credentials found in cache cookbook (Redis password: 'redis_secure_password_123')
  - PostgreSQL credentials in fastapi-tutorial cookbook (database password: 'fastapi_password')
  - SSL certificate paths referenced but certificates not managed by cookbooks
  - 3 modules contain embedded credentials that need Ansible Vault migration

### Technical Challenges

- **Ruby Block Logic**: The cache cookbook contains a ruby_block that performs complex Redis configuration file manipulation - this will need to be converted to Ansible lineinfile or replace modules with appropriate regex patterns
- **Git Repository Management**: FastAPI cookbook clones from external GitHub repository - ensure network access and consider using ansible.builtin.git module with appropriate error handling
- **Service Dependencies**: PostgreSQL must be running before FastAPI application starts - implement proper task ordering and handlers in Ansible
- **Template Migration**: Convert ERB templates (nginx.conf.erb, security.conf.erb, etc.) to Jinja2 format for Ansible

### Migration Order

1. **cache** (low risk, standalone caching services with clear external dependencies)
2. **nginx-multisite** (moderate complexity, security configurations but well-defined scope)
3. **fastapi-tutorial** (high complexity, multiple service dependencies and application deployment)

### Assumptions

- SSL certificates are managed externally and only paths need to be configured in Ansible
- The target environment has internet access for package installation and git repository cloning
- PostgreSQL installation and initial setup can be handled by standard Ansible modules without custom database initialization scripts
- The current Chef Solo deployment model will be replaced with Ansible playbook execution
- UFW firewall rules are appropriate for the target environment and don't conflict with existing security policies
- The Ruby block configuration fixes in the Redis cookbook are still necessary in the target environment
- Vagrant development environment setup is still required and will be converted to Ansible provisioning