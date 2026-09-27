# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with caching, security hardening, and SSL-enabled nginx reverse proxy. The migration involves 3 cookbooks with moderate complexity, estimated timeline of 3-4 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication, memcached integration, custom Redis configuration patching, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment, and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service configuration, environment file management

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening, and fail2ban protection
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security parameters

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx, memcached, redisio)
- `solo.json`: Chef Solo run list and node attributes configuration
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support specified in metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (based on Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or cloud-agnostic deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules and custom configuration management

### Security Considerations

- **Hardcoded credentials**: Redis password and PostgreSQL credentials are embedded in recipes - migrate to Ansible Vault
- **SSL certificate management**: SSL certificate paths configured but certificate provisioning not automated - implement proper certificate management
- **SSH hardening**: Root login disabled, password authentication disabled - preserve in Ansible
- **Firewall configuration**: UFW rules for HTTP/HTTPS/SSH - migrate to ansible.posix.ufw module
- **Fail2ban configuration**: Custom jail configuration - migrate to community.general.fail2ban module
- **Sysctl security parameters**: Kernel security hardening - migrate to ansible.posix.sysctl module

Credential patterns identified:
- Redis: Hardcoded password in recipe (`redis_secure_password_123`)
- PostgreSQL: Hardcoded credentials in recipe (`fastapi:fastapi_password`)
- SSL: Certificate paths configured but certificates not managed

### Technical Challenges

- **Custom Redis configuration patching**: Chef uses ruby_block to modify Redis config file post-installation - requires custom Ansible task with lineinfile or template
- **Git repository synchronization**: Chef git resource behavior needs replication with ansible.builtin.git module
- **Multi-site nginx configuration**: Dynamic site generation from attributes requires Jinja2 templating and loops
- **Service dependency management**: PostgreSQL must be running before database operations - use Ansible handlers and service dependencies
- **File permissions and ownership**: Multiple file/directory operations with specific ownership - ensure proper become/become_user usage

### Migration Order

1. **cache** (low risk, standalone service)
   - Minimal external dependencies
   - Clear service boundaries
   - Good testing candidate

2. **nginx-multisite** (moderate complexity)
   - Security configurations can be validated independently
   - Template migration straightforward
   - Foundation for application services

3. **fastapi-tutorial** (high complexity, dependencies)
   - Depends on PostgreSQL service availability
   - Complex application deployment workflow
   - Integration testing required with nginx-multisite

### Assumptions

- SSL certificates will be provided externally or managed through separate certificate management solution (Let's Encrypt, internal CA)
- PostgreSQL installation and initial configuration is acceptable to run as root user (current Chef implementation)
- Redis and memcached default configurations are sufficient with only the specified customizations
- UFW firewall is the preferred firewall solution (no iptables migration needed)
- Git repository access does not require authentication (public repository)
- Python 3 and pip are available in target system package repositories
- Systemd is the target init system for service management
- Development environment (Vagrant) configuration is not required in Ansible migration
- Target systems have internet access for package installation and git repository cloning
- Current Chef Solo deployment model will be replaced with standard Ansible playbook execution
- No Chef Server integration exists that needs to be replicated