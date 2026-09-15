# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with caching, security hardening, and SSL-enabled nginx reverse proxy. The migration involves 3 cookbooks with moderate complexity, estimated timeline of 3-4 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx web server with multi-site SSL configuration, security hardening via fail2ban/UFW firewall, and SSH hardening with root login disabled
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: SSL-enabled virtual hosts for test/ci/status subdomains, fail2ban intrusion prevention, UFW firewall rules, sysctl security tuning, SSH configuration hardening

**cache**:
- Description: Caching services layer providing both memcached and Redis with authentication and custom configuration patches
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis 6379 with password authentication, memcached service, Redis log directory management, configuration file patching via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python web application with PostgreSQL database backend, systemd service management, and virtual environment setup
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment, PostgreSQL database and user creation, systemd service configuration, environment variable management

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo configuration with run_list and node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo execution configuration
- `Vagrantfile`: Development environment provisioning (requires review for Ansible equivalent)
- `vagrant-provision.sh`: Shell provisioning script for Vagrant integration

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support specified in cookbook metadata)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified (local/on-premises deployment)

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom Redis configuration tasks

### Security Considerations

- **Hardcoded credentials**: Redis password "redis_secure_password_123" and PostgreSQL password "fastapi_password" are embedded in recipes - migrate to Ansible Vault
- **SSL certificate management**: SSL certificates referenced in nginx configuration require secure deployment mechanism via Ansible Vault or external certificate management
- **SSH hardening**: Root login disabled and password authentication disabled - preserve these security settings in Ansible
- **Firewall configuration**: UFW rules for SSH/HTTP/HTTPS need careful migration to ensure no service interruption
- **Fail2ban configuration**: Intrusion prevention settings require template migration and service management
- **Database credentials**: PostgreSQL user creation with embedded passwords needs Ansible Vault integration

### Technical Challenges

- **Ruby block configuration patching**: The cache cookbook uses ruby_block to modify Redis configuration files post-installation - requires conversion to Ansible lineinfile or template modules
- **Multi-site nginx configuration**: Template-driven virtual host generation needs conversion to Ansible jinja2 templates with loop constructs
- **Service dependency management**: PostgreSQL must be running before FastAPI application starts - requires proper Ansible task ordering and handlers
- **Git repository management**: FastAPI tutorial cloning and virtual environment setup needs idempotent Ansible git and pip modules
- **Systemd service creation**: Custom systemd unit files require template conversion and systemctl module usage

### Migration Order

1. **cache** (low risk, foundational service) - Redis and memcached services with minimal external dependencies
2. **nginx-multisite** (moderate complexity) - Web server with security hardening, depends on SSL certificate availability
3. **fastapi-tutorial** (high complexity) - Application deployment with database dependencies and service integration

### Assumptions

- SSL certificates for test.cluster.local, ci.cluster.local, and status.cluster.local domains are available and will be managed outside Ansible or via separate certificate management playbooks
- PostgreSQL installation and initial configuration is acceptable via package manager defaults (no custom compilation or advanced tuning required)
- The FastAPI tutorial Git repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and the main branch is stable
- Target systems have internet access for package installation and Git repository cloning
- The ruby_block configuration patches in the Redis setup are still necessary and the equivalent functionality needs to be replicated in Ansible
- UFW firewall rules can be applied without conflicting with existing iptables or other firewall management systems
- The systemd service configuration for FastAPI is appropriate for the target environment and no additional security contexts (SELinux, AppArmor) need consideration
- The current Chef Solo execution model will be replaced with Ansible playbook execution, potentially requiring inventory and group_vars restructuring