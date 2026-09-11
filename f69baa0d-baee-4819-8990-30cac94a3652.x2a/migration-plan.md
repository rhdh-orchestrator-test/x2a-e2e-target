# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing web services, caching infrastructure, and a FastAPI application. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to multi-service dependencies and security configurations. Estimated timeline: 3-4 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx web server with multi-site SSL configuration, security hardening via fail2ban/UFW, and system-level security controls
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multiple SSL-enabled virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local), fail2ban intrusion prevention, UFW firewall configuration, SSH hardening, sysctl security tuning

**cache**:
- Description: Caching services infrastructure with memcached and Redis, including authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached service, Redis with password authentication (redis_secure_password_123), custom Redis configuration patching via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python web application with PostgreSQL database backend, systemd service management, and virtual environment setup
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning from GitHub, Python virtual environment creation, PostgreSQL database and user provisioning, systemd service configuration, environment variable management

### Infrastructure Files

- `Berksfile`: Chef cookbook dependency management with external dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list configuration and node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file for cookbook paths and execution settings
- `Vagrantfile`: Development environment provisioning with Vagrant
- `vagrant-provision.sh`: Shell script for Vagrant VM provisioning automation

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support specified in cookbook metadata)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or VM-based deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis or ansible.builtin.template for custom Redis configuration
- **ssl_certificate (~> 2.1)**: Currently commented out, but SSL management will need ansible.builtin.copy or community.crypto.* modules

### Security Considerations

- **Hardcoded credentials**: Redis password (redis_secure_password_123) and PostgreSQL password (fastapi_password) are embedded in recipes - migrate to Ansible Vault
- **SSL certificate management**: SSL paths configured but certificate deployment method unclear - implement with ansible.builtin.copy or community.crypto modules
- **SSH hardening**: Root login disabled, password authentication disabled - migrate to ansible.posix.sysctl and ansible.builtin.lineinfile
- **Firewall configuration**: UFW rules for SSH, HTTP, HTTPS - migrate to community.general.ufw module
- **Fail2ban configuration**: Intrusion prevention with custom jail.local template - migrate to ansible.builtin.template
- **System security**: Custom sysctl parameters via template - migrate to ansible.posix.sysctl module

### Technical Challenges

- **Ruby block configuration patching**: The cache cookbook uses a ruby_block to manually edit Redis configuration files, removing specific lines - this will need conversion to ansible.builtin.lineinfile with state=absent or custom Jinja2 template logic
- **Multi-service coordination**: The nginx-multisite cookbook orchestrates multiple services (nginx, fail2ban, ufw, ssh) with complex notification chains - requires careful Ansible handler design
- **Git repository management**: FastAPI cookbook clones from GitHub with sync action - migrate to ansible.builtin.git module with appropriate version control
- **PostgreSQL user/database creation**: Uses shell commands with sudo -u postgres - migrate to community.postgresql.* modules for idempotent database management
- **Systemd service creation**: Custom service file creation and daemon-reload - migrate to ansible.builtin.systemd and ansible.builtin.template

### Migration Order

1. **cache** (low risk, standalone service with clear dependencies)
2. **fastapi-tutorial** (moderate complexity, database dependencies but isolated application)
3. **nginx-multisite** (high complexity, multiple security configurations and service dependencies)

### Assumptions

- SSL certificates are managed externally or will be provided during Ansible deployment (certificate deployment method not visible in current Chef configuration)
- The GitHub repository for FastAPI tutorial (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and the 'main' branch is stable
- Target systems have internet access for package installation and git repository cloning
- PostgreSQL installation method (package vs. custom compilation) is acceptable via standard package managers
- The custom Redis configuration patching in the ruby_block is still necessary and not resolved by newer Redis versions
- UFW firewall rules are appropriate for the target environment and no additional ports need to be opened
- The fail2ban jail.local template contains appropriate configuration (template content not reviewed in this analysis)
- Systemd is the target init system for service management
- The nginx sites (test.cluster.local, ci.cluster.local, status.cluster.local) are internal domains and DNS resolution is handled externally