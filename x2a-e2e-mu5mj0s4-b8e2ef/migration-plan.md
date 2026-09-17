# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with 3 cookbooks managing web services, caching infrastructure, and a FastAPI application. The migration involves converting Chef cookbooks to Ansible roles, replacing external cookbook dependencies with Ansible collections, and adapting Chef-specific patterns to Ansible best practices. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached installation via external cookbook, Redis with password authentication, custom Redis configuration patching, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database backend, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service management, environment configuration file

**nginx-multisite**:
- Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and fail2ban protection
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site configuration (test.cluster.local, ci.cluster.local, status.cluster.local), SSL certificate management, fail2ban jail configuration, UFW firewall rules, SSH security hardening, sysctl security parameters

### Infrastructure Files

- `Berksfile`: Chef cookbook dependency management - needs conversion to Ansible requirements.yml
- `solo.json`: Chef node configuration and run list - needs conversion to Ansible inventory and playbook
- `solo.rb`: Chef Solo configuration - replaced by ansible.cfg
- `Vagrantfile`: Development environment provisioning - may need Ansible provisioner updates
- `vagrant-provision.sh`: Shell provisioning script - can be integrated into Ansible playbooks

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox (based on Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be local/on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **memcached (~> 6.0)**: Replace with ansible.builtin.package and memcached configuration tasks
- **redisio (~> 7.2.4)**: Replace with community.general.redis or custom Redis installation and configuration tasks
- **nginx (~> 12.0)**: Replace with nginxinc.nginx_core collection or custom nginx configuration

### Security Considerations

- **Hardcoded credentials**: Redis password "redis_secure_password_123" and PostgreSQL password "fastapi_password" are hardcoded in recipes - migrate to Ansible Vault
- **SSL certificate management**: SSL certificates referenced in nginx configuration need secure deployment mechanism via Ansible Vault
- **SSH security**: Root login disabled and password authentication disabled - maintain these security settings in Ansible
- **Firewall configuration**: UFW rules for HTTP/HTTPS/SSH - convert to ansible.posix.ufw module
- **Fail2ban configuration**: Jail configuration for nginx protection - convert to fail2ban Ansible role
- **Sysctl security parameters**: Kernel security hardening - convert to ansible.posix.sysctl module

### Technical Challenges

- **Redis configuration patching**: The cache cookbook uses a Ruby block to manually edit Redis configuration files post-installation - this needs to be converted to proper Ansible template management or lineinfile modules
- **PostgreSQL database initialization**: Chef execute blocks for database/user creation need conversion to postgresql Ansible modules with proper idempotency
- **Multi-site nginx configuration**: Template-driven site configuration needs conversion to Ansible jinja2 templates with proper variable structure
- **Service dependencies**: Systemd service ordering and dependencies need proper Ansible service module configuration
- **Git repository management**: FastAPI application deployment via git needs conversion to ansible.builtin.git module with proper change detection

### Migration Order

1. **cache** (moderate complexity, standalone caching services)
2. **nginx-multisite** (high complexity due to security configurations and multi-site setup)
3. **fastapi-tutorial** (moderate complexity, depends on database setup and application deployment patterns)

### Assumptions

- SSL certificates are manually managed and placed in standard locations (/etc/ssl/certs, /etc/ssl/private)
- The FastAPI tutorial repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and stable
- Current Chef Solo deployment model will be replaced with Ansible playbook execution
- Vagrant development environment will continue to be used with Ansible provisioner
- Target systems have sudo access for package installation and service management
- Database passwords and Redis authentication will be migrated to Ansible Vault for security
- The three virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local) represent the complete site configuration requirements
- UFW firewall is the preferred firewall solution and will be maintained in the Ansible version
- Fail2ban configuration is critical for production security and must be preserved
- The custom Redis configuration fixes in the Ruby block represent necessary workarounds that need to be properly addressed in Ansible templates