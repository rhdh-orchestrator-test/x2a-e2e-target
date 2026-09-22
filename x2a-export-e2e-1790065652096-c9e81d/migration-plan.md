# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with caching, security hardening, and SSL-enabled nginx reverse proxy. The migration involves 3 cookbooks with moderate complexity, requiring approximately 4-6 weeks for a complete migration including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including authentication and custom Redis configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis password authentication, custom log directory creation, configuration file patching via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python venv creation, PostgreSQL database and user provisioning, systemd service management

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening, and fail2ban protection
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, self-signed certificate generation, fail2ban integration, UFW firewall rules, SSH hardening

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list configuration and node attributes for site definitions and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support specified in metadata.rb files)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be infrastructure-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom Redis configuration tasks

### Security Considerations

- **Hardcoded credentials**: Redis password "redis_secure_password_123" and PostgreSQL password "fastapi_password" are embedded in recipes - migrate to Ansible Vault
- **SSL certificate management**: Self-signed certificates generated via OpenSSL commands - consider Let's Encrypt integration with community.crypto collection
- **SSH hardening**: Root login disabled, password authentication disabled - migrate to ansible.posix.sshd_config module
- **Firewall configuration**: UFW rules for HTTP/HTTPS/SSH - migrate to community.general.ufw module
- **Fail2ban integration**: Custom jail configuration - migrate to community.general.fail2ban module
- **Credential types per module**:
  - cache: Redis authentication password
  - fastapi-tutorial: PostgreSQL database credentials, application environment variables
  - nginx-multisite: SSL certificate generation, no stored credentials

### Technical Challenges

- **Ruby block configuration patching**: The cache cookbook uses ruby_block to modify Redis configuration files post-installation - requires custom Ansible tasks with lineinfile or template modules
- **Multi-site SSL certificate generation**: Dynamic certificate creation per site requires Ansible loops and conditional logic
- **Service dependency management**: PostgreSQL must be running before FastAPI application starts - use Ansible handlers and service dependencies
- **Git repository synchronization**: FastAPI cookbook clones and syncs git repositories - migrate to ansible.builtin.git module with proper change detection
- **Python virtual environment management**: Complex pip installation within venv requires ansible.builtin.pip with virtualenv parameters

### Migration Order

1. **nginx-multisite** (foundational infrastructure, moderate complexity)
2. **cache** (independent caching layer, requires custom Redis configuration handling)
3. **fastapi-tutorial** (application layer, depends on database and potentially cache services)

### Assumptions

- SSL certificates are self-signed for development/testing environments - production deployment may require different certificate management strategy
- Database credentials are acceptable for development but will need Ansible Vault encryption for production
- UFW firewall is the preferred firewall solution (vs iptables or firewalld)
- Redis configuration patching via ruby_block suggests upstream cookbook limitations that may not apply to Ansible Redis modules
- Multi-platform support (Ubuntu/CentOS) will be maintained in Ansible playbooks
- Vagrant development environment workflow will be preserved or replaced with equivalent Ansible testing approach
- Current Chef Solo execution model suggests single-node deployments rather than multi-node orchestration
- Site-specific static files (index.html for test/ci/status sites) are simple placeholders and not complex applications
- PostgreSQL database initialization is idempotent and safe to re-run
- SystemD is available on target systems for service management
- The application expects to run as root user (may need security review for production)