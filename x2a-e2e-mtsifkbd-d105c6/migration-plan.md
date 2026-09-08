# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with caching, security hardening, and SSL-enabled nginx reverse proxy. The migration involves 3 cookbooks with moderate complexity, requiring approximately 4-6 weeks for complete migration including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including authentication, logging, and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication, memcached integration, custom Redis config patching, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service management, environment configuration

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening, and fail2ban protection
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, self-signed certificate generation, fail2ban integration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo configuration with run list and attribute overrides for site configurations and security settings
- `solo.rb`: Chef Solo execution configuration
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support specified in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (based on Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be VM-based deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules and custom configuration management

### Security Considerations

- **Hardcoded Credentials**: Redis password ('redis_secure_password_123') and PostgreSQL credentials ('fastapi_password') are embedded in recipes - migrate to Ansible Vault
- **SSL Certificate Management**: Self-signed certificates generated via OpenSSL commands - consider Let's Encrypt integration or proper certificate management
- **SSH Hardening**: Root login disabled, password authentication disabled - preserve these security configurations
- **Firewall Configuration**: UFW rules for HTTP/HTTPS/SSH - migrate to ansible.posix.ufw module
- **Fail2ban Integration**: Custom jail configuration for nginx protection - migrate templates to Jinja2
- **Sysctl Security Tuning**: Kernel parameter hardening via template - preserve security settings

### Technical Challenges

- **Custom Redis Configuration Patching**: The cache cookbook includes a Ruby block that manually edits Redis config files to remove specific directives - this will need custom Ansible lineinfile tasks or template management
- **Multi-site SSL Certificate Generation**: Dynamic certificate creation for multiple domains requires loop-based certificate generation with proper file permissions
- **Service Dependencies**: FastAPI service depends on PostgreSQL being ready - implement proper service ordering and health checks
- **Git Repository Management**: FastAPI cookbook clones from GitHub - ensure proper git module usage with version pinning
- **Template Migration**: Multiple ERB templates need conversion to Jinja2 (nginx.conf, security.conf, fail2ban.jail.local, sysctl-security.conf, site.conf)

### Migration Order

1. **cache** (low risk, foundational service) - Redis and memcached are well-supported in Ansible with established modules
2. **nginx-multisite** (moderate complexity) - Complex SSL and security configuration but well-documented Ansible patterns exist
3. **fastapi-tutorial** (high complexity) - Application deployment with database dependencies and custom service management

### Assumptions

- Target environments will maintain Ubuntu/CentOS compatibility as specified in cookbook metadata
- Self-signed certificates are acceptable for development; production may require proper CA-signed certificates or Let's Encrypt
- PostgreSQL and Redis passwords can be migrated to Ansible Vault without changing the actual credential values
- The custom Redis configuration patching in the cache cookbook is still necessary and not resolved by newer Redis versions
- Git repository access for FastAPI tutorial remains available and accessible from target environments
- Systemd is available on target systems for service management (implied by Ubuntu 18.04+ and CentOS 7+ support)
- UFW firewall is the preferred firewall solution (rather than iptables or firewalld)
- The current Chef Solo execution model will be replaced with standard Ansible playbook execution