# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with caching, security hardening, and SSL-enabled nginx reverse proxy. The migration involves 3 cookbooks with moderate complexity, estimated timeline of 3-4 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis authentication, includes Redis log directory setup and configuration file patching
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached integration, Redis with password authentication (redis_secure_password_123), custom Redis configuration patching, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service management, environment configuration file

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening with fail2ban and UFW firewall, SSH configuration lockdown
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, self-signed certificate generation, fail2ban integration, UFW firewall rules, SSH security hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list configuration and attribute overrides for site definitions and security settings
- `solo.rb`: Chef Solo configuration file for local cookbook execution
- `Vagrantfile`: Development environment provisioning with Vagrant
- `vagrant-provision.sh`: Shell script for Vagrant VM provisioning

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support specified in metadata.rb files)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or cloud-agnostic deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks

### Security Considerations

- **Hardcoded Credentials**: Redis password (redis_secure_password_123) and PostgreSQL credentials (fastapi:fastapi_password) are embedded in recipes - migrate to Ansible Vault
- **SSL Certificate Management**: Self-signed certificates generated via OpenSSL commands - consider Let's Encrypt integration with community.crypto.acme_certificate
- **SSH Security Configuration**: Root login disabled, password authentication disabled - maintain with ansible.posix.sshd_config
- **Firewall Rules**: UFW configuration for HTTP/HTTPS/SSH - migrate to community.general.ufw module
- **Fail2ban Configuration**: Custom jail.local template - migrate to community.general.fail2ban module
- **Credential Types per Module**:
  - cache: Redis authentication password
  - fastapi-tutorial: PostgreSQL database credentials, application environment variables
  - nginx-multisite: SSL certificate generation, no stored credentials but certificate management

### Technical Challenges

- **Redis Configuration Patching**: The cache cookbook includes a Ruby block that manually edits Redis configuration files to remove specific directives - this will need custom Ansible lineinfile tasks or template replacement
- **Multi-site SSL Certificate Generation**: Dynamic certificate generation for multiple domains requires loop-based certificate creation with proper file permissions and ownership
- **Service Dependencies**: FastAPI service depends on PostgreSQL being available - ensure proper task ordering and service dependency management in Ansible
- **Template Migration**: ERB templates need conversion to Jinja2 format, particularly nginx.conf.erb and security configuration templates

### Migration Order

1. **cache** (low risk, standalone service) - Redis and memcached services with minimal external dependencies
2. **nginx-multisite** (moderate complexity) - Web server configuration with security hardening, depends on SSL certificate generation
3. **fastapi-tutorial** (high complexity) - Application deployment with database dependencies, Git integration, and service management

### Assumptions

- Target environments will maintain the same OS support (Ubuntu 18.04+, CentOS 7+) as specified in Chef metadata
- Self-signed certificates are acceptable for development/testing environments - production may require CA-signed or Let's Encrypt certificates
- PostgreSQL and Redis password authentication requirements will remain the same in target environment
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) will remain accessible during migration
- Current firewall rules (SSH, HTTP, HTTPS) are sufficient and no additional ports need to be opened
- The three-site configuration (test.cluster.local, ci.cluster.local, status.cluster.local) represents the complete scope of nginx virtual hosts
- Systemd is available on target systems for service management (implied by Ubuntu 18.04+ and CentOS 7+ support)
- Root user execution context is acceptable for application deployment (as used in fastapi-tutorial cookbook)