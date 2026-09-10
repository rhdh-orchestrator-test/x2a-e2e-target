# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing web services, caching infrastructure, and a FastAPI application. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to security configurations, SSL management, and database setup. Estimated timeline: 3-4 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx web server with multi-site SSL configuration, security hardening via fail2ban/UFW, and system-level security controls including SSH hardening and sysctl tuning
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: SSL-enabled virtual hosts for test/ci/status subdomains, fail2ban jail configuration, UFW firewall rules, SSH security hardening, sysctl security parameters

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached service setup, Redis with password authentication, custom Redis configuration cleanup via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python application deployment with PostgreSQL database, virtual environment setup, and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment, PostgreSQL database and user creation, systemd service configuration, environment file management

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4) and local cookbook paths
- `solo.json`: Chef Solo run list configuration and node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file (not examined but likely contains cookbook paths and cache settings)
- `Vagrantfile`: Development environment provisioning (not examined but indicates Vagrant-based testing)
- `vagrant-provision.sh`: Vagrant provisioning script for development setup

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant-based development environment (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be generic Linux deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx installation and configuration
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules for memcached setup
- **redisio (~> 7.2.4)**: Replace with ansible.builtin.package, ansible.builtin.template, and ansible.builtin.lineinfile modules for Redis configuration and the custom configuration cleanup logic

### Security Considerations

- **Hardcoded credentials**: Redis password ('redis_secure_password_123') and PostgreSQL credentials ('fastapi_password') are embedded in recipe code - migrate to Ansible Vault
- **SSL certificate management**: SSL certificate and private key paths are configured but certificate provisioning method is unclear - requires investigation of actual certificate deployment strategy
- **SSH security hardening**: Root login disable and password authentication disable via sed commands - migrate to ansible.posix.sshd_config module
- **Firewall configuration**: UFW rules for SSH, HTTP, HTTPS - migrate to community.general.ufw module
- **System security**: fail2ban configuration and sysctl security parameters - migrate to appropriate Ansible modules
- **Database credentials**: PostgreSQL user creation with embedded password - migrate to Ansible Vault with postgresql_user module

### Technical Challenges

- **Ruby block configuration cleanup**: The cache cookbook contains a ruby_block that performs regex-based Redis configuration cleanup - this custom logic needs to be replicated using Ansible's lineinfile or replace modules with appropriate regex patterns
- **Git repository synchronization**: FastAPI cookbook uses Chef's git resource with sync action - migrate to ansible.builtin.git module with appropriate version control handling
- **Service dependency management**: Multiple services (nginx, postgresql, redis, memcached) with interdependencies - ensure proper task ordering and handler configuration in Ansible
- **Template migration**: ERB templates need conversion to Jinja2 format, particularly nginx.conf.erb, security.conf.erb, and fail2ban.jail.local.erb

### Migration Order

1. **cache** (low risk, foundational service) - Start with caching services as they have fewer dependencies and simpler configuration
2. **nginx-multisite** (moderate complexity) - Web server with security configurations, depends on understanding SSL certificate deployment
3. **fastapi-tutorial** (high complexity) - Application deployment with database dependencies, systemd service management, and git integration

### Assumptions

- SSL certificates are manually deployed or managed outside of this configuration (no certificate generation/renewal logic found in the cookbooks)
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) is accessible and the requirements.txt file exists
- PostgreSQL service is expected to be running on the same host as the FastAPI application
- The target environment has internet access for package installation and git repository cloning
- UFW is the preferred firewall solution (rather than iptables or firewalld)
- The nginx sites (test.cluster.local, ci.cluster.local, status.cluster.local) resolve to the target host
- Static HTML files in cookbooks/nginx-multisite/files/default/ represent the actual site content to be deployed
- The Redis configuration cleanup in the cache cookbook is still necessary in the target environment
- Development and production environments use similar configurations (based on Vagrant setup presence)