# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with caching services, security hardening, and SSL-enabled nginx reverse proxy. The migration involves 3 cookbooks with moderate complexity, external dependencies on Chef Supermarket cookbooks, and embedded security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis password authentication, custom log directory creation, configuration file patching via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment setup, and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment, PostgreSQL database and user creation, systemd service configuration

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening, and static site hosting
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site configuration, SSL certificate management, fail2ban integration, UFW firewall rules, SSH hardening

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list and node attributes configuration with site definitions and security settings
- `solo.rb`: Chef Solo configuration file for local cookbook execution
- `Vagrantfile`: Development environment provisioning (requires review for Ansible equivalent)
- `vagrant-provision.sh`: Shell script for Vagrant VM provisioning

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox (based on Vagrantfile presence)
- **Cloud Platform**: Not specified (local development focus)

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom Redis configuration tasks
- **Chef Supermarket cookbooks**: All external dependencies need equivalent Ansible roles from Ansible Galaxy or custom implementation

### Security Considerations

- **Hardcoded credentials**: Redis password "redis_secure_password_123" and PostgreSQL password "fastapi_password" are embedded in recipes
- **SSH hardening**: Root login disabled, password authentication disabled via direct sshd_config modification
- **Firewall management**: UFW rules for SSH (22), HTTP (80), HTTPS (443) with default deny policy
- **Fail2ban integration**: Custom jail.local configuration for intrusion prevention
- **SSL certificate management**: Certificate and private key paths defined but certificate provisioning not visible in reviewed files
- **Sysctl security tuning**: Custom kernel parameter hardening via template

### Technical Challenges

- **Ruby block configuration patching**: The cache cookbook uses ruby_block to modify Redis configuration files post-installation, requiring equivalent Ansible lineinfile or replace modules
- **Multi-cookbook orchestration**: The solo.json run list coordinates three cookbooks that must be properly sequenced in Ansible playbooks
- **Template migration**: ERB templates (nginx.conf.erb, security.conf.erb, site.conf.erb) need conversion to Jinja2 format
- **Git repository management**: FastAPI cookbook clones from GitHub, requiring ansible.builtin.git module with proper authentication handling
- **Service dependency management**: PostgreSQL must be running before FastAPI application starts, requiring proper Ansible task ordering

### Migration Order

1. **cache** (low risk, standalone caching services with clear external dependencies)
2. **nginx-multisite** (moderate complexity, security configurations require careful testing)
3. **fastapi-tutorial** (high complexity, database dependencies and application deployment coordination)

### Assumptions

- SSL certificates are managed externally or through a separate process not visible in the reviewed cookbook files
- The Git repository https://github.com/dibanez/fastapi_tutorial.git is accessible and contains the expected requirements.txt file
- PostgreSQL installation uses default package manager repositories rather than custom sources
- The target environment has internet access for package installation and Git repository cloning
- UFW firewall rules are appropriate for the target network environment
- The custom Redis configuration patching in the ruby_block is still necessary and not resolved by newer Redis packages
- Systemd is the target service manager (based on the FastAPI service file creation)
- The www-data user and group exist on target systems for nginx file ownership