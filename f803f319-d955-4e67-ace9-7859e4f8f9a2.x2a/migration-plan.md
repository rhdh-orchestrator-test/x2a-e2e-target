# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing web services, caching infrastructure, and a Python application stack. The migration involves converting Chef cookbooks to Ansible playbooks and roles, addressing external dependencies, and maintaining security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx reverse proxy with SSL-enabled multi-site hosting, security hardening via fail2ban/UFW, and system-level security configurations
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-domain SSL sites (test.cluster.local, ci.cluster.local, status.cluster.local), fail2ban intrusion prevention, UFW firewall rules, SSH hardening, sysctl security tuning

**cache**:
- Description: Caching services infrastructure providing both memcached and Redis with authentication and custom configuration management
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication, memcached service, custom Redis configuration patching, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application with PostgreSQL database backend, systemd service management, and virtual environment setup
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment, PostgreSQL database and user creation, systemd service configuration, environment variable management

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo configuration with run list and node attributes for site configurations and security settings
- `solo.rb`: Chef Solo configuration file (likely contains cookbook paths and cache settings)
- `Vagrantfile`: Development environment provisioning for local testing
- `vagrant-provision.sh`: Shell script for Vagrant VM provisioning

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be platform-agnostic infrastructure

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks
- **Chef Supermarket cookbooks**: All external dependencies need Ansible equivalents from Ansible Galaxy or custom role development

### Security Considerations

- **Hardcoded credentials**: Redis password ('redis_secure_password_123') and PostgreSQL credentials ('fastapi_password') are embedded in recipes and need Ansible Vault encryption
- **SSL certificate management**: SSL certificate paths and configuration need migration to ansible.builtin.copy or community.crypto modules
- **SSH hardening**: Root login disable and password authentication disable configurations need migration to ansible.posix.sshd_config
- **Firewall rules**: UFW commands need conversion to community.general.ufw module
- **Fail2ban configuration**: Template-based jail.local configuration needs migration to ansible.builtin.template
- **Credential types per module**:
  - nginx-multisite: SSH configuration, SSL certificates
  - cache: Redis authentication password
  - fastapi-tutorial: PostgreSQL database credentials, application environment variables

### Technical Challenges

- **Complex Redis configuration patching**: The cache cookbook uses a Ruby block to manually edit Redis config files, requiring custom Ansible tasks with ansible.builtin.lineinfile or ansible.builtin.replace modules
- **Multi-site nginx configuration**: Template-driven site configuration with dynamic document root creation needs careful conversion to Ansible loops and templates
- **PostgreSQL database initialization**: Chef's execute resources for database/user creation need conversion to community.postgresql modules with proper idempotency
- **Systemd service management**: Custom systemd service file creation and daemon-reload operations need ansible.builtin.systemd module integration
- **Git repository management**: FastAPI application deployment via git clone needs ansible.builtin.git module with proper change detection

### Migration Order

1. **cache** (low risk, isolated caching services with clear external dependencies)
2. **fastapi-tutorial** (moderate complexity, database integration but self-contained application)
3. **nginx-multisite** (high complexity, security configurations and multi-site template management with dependencies on other services)

### Assumptions

- SSL certificates are manually managed and placed in standard system paths (/etc/ssl/certs, /etc/ssl/private)
- The target environment has internet access for package installation and git repository cloning
- PostgreSQL service is expected to be managed by the system package manager (apt/yum)
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and stable
- UFW and fail2ban are the preferred security tools for the target environment
- The nginx sites (test.cluster.local, ci.cluster.local, status.cluster.local) have DNS resolution configured externally
- Static HTML files for each site are provided in the cookbook files directory and need migration to Ansible file resources
- The target systems have systemd as the init system for service management
- Python 3 virtual environment approach is preferred over system-wide package installation
- Redis and memcached will continue to run on default ports with the same authentication requirements