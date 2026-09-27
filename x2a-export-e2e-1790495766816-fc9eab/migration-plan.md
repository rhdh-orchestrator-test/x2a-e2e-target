# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with nginx reverse proxy, caching services (Redis/Memcached), and a FastAPI application with PostgreSQL backend. The migration involves 3 custom cookbooks with moderate complexity, requiring approximately 4-6 weeks for a complete migration including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx web server with multi-site SSL configuration, security hardening (fail2ban, UFW firewall), and SSH security controls
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Self-signed SSL certificates for 3 subdomains (test/ci/status.cluster.local), fail2ban intrusion prevention, UFW firewall rules, SSH hardening (root login disabled, password auth disabled), sysctl security tuning

**cache**:
- Description: Caching services configuration with Redis and Memcached for application performance optimization
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis server with authentication (port 6379), Memcached service, custom Redis configuration cleanup via ruby_block, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database backend and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Python 3 virtual environment, Git repository cloning from GitHub, PostgreSQL database and user creation, systemd service configuration, environment variable management

### Infrastructure Files

- `Berksfile`: Chef dependency management - defines external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo node configuration with run_list and attribute overrides for nginx sites and security settings
- `solo.rb`: Chef Solo configuration file for cookbook paths and node attributes
- `Vagrantfile`: Development environment provisioning for local testing
- `vagrant-provision.sh`: Shell script for Vagrant VM provisioning

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (based on Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be infrastructure-agnostic

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx configuration
- **memcached (~> 6.0)**: Replace with community.general.memcached or ansible.builtin.package for memcached installation
- **redisio (~> 7.2.4)**: Replace with community.general.redis or ansible.builtin.package with custom configuration templates

### Security Considerations

- **Hardcoded credentials**: Redis password "redis_secure_password_123" and PostgreSQL password "fastapi_password" are hardcoded in recipes - migrate to Ansible Vault
- **SSL certificate management**: Self-signed certificates generated via OpenSSL commands - consider Let's Encrypt integration or proper certificate management
- **SSH security configurations**: Root login disabled, password authentication disabled - preserve these security settings in Ansible
- **Firewall rules**: UFW configuration for ports 22, 80, 443 - migrate to ansible.posix.ufw module
- **Fail2ban configuration**: Intrusion prevention via template - migrate to ansible.builtin.template with fail2ban.jail.local.erb content
- **Credential patterns per module**:
  - nginx-multisite: SSL certificate paths, no embedded credentials
  - cache: Redis authentication password (hardcoded)
  - fastapi-tutorial: PostgreSQL credentials (hardcoded), GitHub repository access

### Technical Challenges

- **Ruby block workarounds**: The cache cookbook contains a ruby_block hack to fix Redis configuration - this custom logic needs to be replicated using Ansible's lineinfile or replace modules
- **Complex service dependencies**: FastAPI service depends on PostgreSQL being ready - implement proper service ordering and health checks in Ansible
- **Multi-site SSL management**: Dynamic SSL certificate generation for multiple subdomains requires loop-based certificate creation in Ansible
- **Template migration**: Convert 5 ERB templates (nginx.conf, security.conf, site.conf, fail2ban.jail.local, sysctl-security.conf) to Jinja2 format
- **Git repository management**: FastAPI cookbook clones from GitHub - ensure proper git module usage with revision tracking

### Migration Order

1. **cache** (Priority 1: Low risk, standalone service, clear dependencies)
2. **nginx-multisite** (Priority 2: Moderate complexity, security-critical, foundation for other services)
3. **fastapi-tutorial** (Priority 3: High complexity, depends on database setup, application-specific logic)

### Assumptions

- Target environments will maintain Ubuntu/CentOS compatibility as specified in cookbook metadata
- Self-signed certificates are acceptable for development/testing environments (production may require proper CA-signed certificates)
- Current hardcoded passwords are acceptable for migration (should be moved to Ansible Vault post-migration)
- The ruby_block Redis configuration hack indicates potential compatibility issues that may need investigation in target Redis versions
- Vagrant development workflow will be replaced with Ansible-based testing (molecule or similar)
- The GitHub repository for FastAPI tutorial (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and the 'main' branch is stable
- Current firewall rules (SSH, HTTP, HTTPS only) are sufficient for the target environment security requirements
- PostgreSQL database initialization can be handled by Ansible postgresql modules without the current shell command approach