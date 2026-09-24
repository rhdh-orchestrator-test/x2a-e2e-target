# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with 3 cookbooks managing web services, caching infrastructure, and a Python application stack. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to multi-service coordination, SSL certificate management, and database integration. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including authentication, logging, and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis password authentication, custom log directory creation, configuration file patching via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python venv setup, PostgreSQL database and user creation, systemd service management

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening, and fail2ban integration
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, self-signed certificate generation, UFW firewall rules, fail2ban jail configuration, SSH hardening

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list and node attributes configuration for all three cookbooks
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support specified in metadata.rb files)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or cloud-agnostic deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom Redis configuration tasks

### Security Considerations

- **Hardcoded credentials**: Redis password "redis_secure_password_123" and PostgreSQL password "fastapi_password" are hardcoded in recipes - migrate to Ansible Vault
- **SSL certificate management**: Self-signed certificates generated via OpenSSL commands - consider Let's Encrypt integration or proper certificate management
- **SSH hardening**: Root login disabled, password authentication disabled - preserve in Ansible tasks
- **Firewall configuration**: UFW rules for SSH, HTTP, HTTPS - migrate to ansible.posix.ufw module
- **Fail2ban integration**: Custom jail configuration for nginx protection - migrate templates to Jinja2
- **Credential types per module**:
  - cache: Redis authentication password
  - fastapi-tutorial: PostgreSQL database credentials, application environment variables
  - nginx-multisite: SSL certificate generation, no stored credentials

### Technical Challenges

- **Ruby block configuration patching**: The cache cookbook uses ruby_block to modify Redis config files post-installation - requires custom Ansible tasks with lineinfile or replace modules
- **Multi-service coordination**: nginx-multisite cookbook orchestrates multiple services (nginx, fail2ban, ufw, ssh) - requires careful task ordering and handlers in Ansible
- **Template migration**: ERB templates need conversion to Jinja2 format, particularly nginx.conf.erb and security configurations
- **Git repository management**: FastAPI cookbook clones and manages git repositories - use ansible.builtin.git module with proper change detection
- **Systemd service creation**: Custom systemd unit files require template migration and proper service management

### Migration Order

1. **cache** (low risk, standalone service) - Redis and memcached setup with minimal external dependencies
2. **fastapi-tutorial** (moderate complexity) - Application deployment with database integration, depends on successful database setup
3. **nginx-multisite** (high complexity, multiple dependencies) - Web server with SSL, security hardening, and firewall configuration that may depend on backend services

### Assumptions

- Target environments will maintain Ubuntu/CentOS compatibility as specified in Chef metadata
- Self-signed certificates are acceptable for development; production may require proper CA-signed certificates
- PostgreSQL and Redis services can be managed by Ansible without external orchestration
- Current hardcoded passwords are development-only and will be replaced with proper secret management
- UFW firewall is the preferred firewall solution (vs. iptables or firewalld)
- Systemd is available on target systems for service management
- Git repository access for FastAPI tutorial code will remain available during migration
- Chef Solo configuration approach suggests single-node deployments rather than multi-node orchestration