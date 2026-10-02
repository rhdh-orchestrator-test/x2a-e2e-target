# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with 3 cookbooks managing web services, caching infrastructure, and a Python application stack. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to multi-service dependencies and security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx reverse proxy with SSL-enabled multi-site hosting, security hardening via fail2ban/UFW, and self-signed certificate generation for development environments
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-domain SSL termination, fail2ban intrusion prevention, UFW firewall configuration, SSH hardening, sysctl security tuning, self-signed certificate generation

**cache**:
- Description: Dual caching service configuration with memcached and Redis, including Redis authentication and custom configuration patching
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached service setup, Redis with password authentication, custom Redis configuration fixes via ruby_block, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database backend, systemd service management, and virtual environment isolation
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service configuration, environment variable management

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list configuration and node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file for local cookbook execution
- `Vagrantfile`: Development environment provisioning (requires review for Ansible conversion)
- `vagrant-provision.sh`: Shell provisioning script for Vagrant integration

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support specified in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be VM-based deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom Redis configuration tasks

### Security Considerations

- **Hardcoded credentials**: Redis password "redis_secure_password_123" and PostgreSQL password "fastapi_password" are hardcoded in recipes - migrate to Ansible Vault
- **SSL certificate management**: Self-signed certificates generated via OpenSSL commands - consider Let's Encrypt integration or proper certificate management
- **SSH hardening**: Root login disabled, password authentication disabled - preserve in Ansible with ansible.posix.sshd_config module
- **Firewall configuration**: UFW rules for HTTP/HTTPS/SSH - migrate to community.general.ufw module
- **Fail2ban configuration**: Intrusion prevention with custom jail.local template - migrate to community.general.fail2ban module
- **Sysctl security tuning**: Custom kernel parameters via template - migrate to ansible.posix.sysctl module
- **Credential types per module**:
  - nginx-multisite: SSL private keys, SSH configuration
  - cache: Redis authentication password
  - fastapi-tutorial: PostgreSQL database credentials, application environment variables

### Technical Challenges

- **Ruby block workarounds**: The cache cookbook uses ruby_block to patch Redis configuration files post-installation - requires conversion to Ansible lineinfile or template tasks
- **Multi-site SSL management**: Dynamic SSL certificate generation for multiple domains requires Ansible loops and conditional logic
- **Service dependencies**: FastAPI application depends on PostgreSQL being ready - implement proper service ordering with ansible.builtin.wait_for
- **Git repository management**: FastAPI cookbook clones from GitHub - ensure proper SSH key or token management for private repositories
- **Template conversion**: ERB templates need conversion to Jinja2 format for nginx.conf, security.conf, fail2ban.jail.local, and site.conf

### Migration Order

1. **cache** (low risk, standalone service) - Independent caching services with minimal external dependencies
2. **nginx-multisite** (moderate complexity) - Web server foundation with security hardening, required by other services
3. **fastapi-tutorial** (high complexity, dependencies) - Application stack requiring database setup and service coordination

### Assumptions

- Current Chef cookbooks are actively used in production environments requiring like-for-like functionality preservation
- SSL certificates are currently self-signed for development - production deployment may require different certificate management strategy
- PostgreSQL and Redis passwords are acceptable to be stored in Ansible Vault rather than external secret management systems
- UFW firewall rules are sufficient for the target environment security requirements
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and the 'main' branch is stable
- Target systems have internet access for package installation and git repository cloning
- Systemd is available on target systems for service management (Ubuntu 18.04+ and CentOS 7+ support confirmed)
- The ruby_block configuration fixes in the Redis setup are still necessary and not resolved in newer Redis versions
- Vagrant development environment workflow should be preserved or replaced with equivalent Ansible-based local testing