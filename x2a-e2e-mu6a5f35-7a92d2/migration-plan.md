# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with caching, security hardening, and SSL-enabled nginx reverse proxy. The migration involves 3 cookbooks with moderate complexity, estimated timeline of 2-3 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis 6379 with authentication, custom log directory setup, and configuration file patching
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis authentication (requirepass), memcached integration, Redis log directory management, configuration file post-processing

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment setup, and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python venv creation, PostgreSQL database/user provisioning, systemd service configuration, environment file management

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening via fail2ban/UFW, and self-signed certificate generation
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site configuration (test/ci/status.cluster.local), SSL certificate generation, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list and node attributes configuration for all three cookbooks
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox (based on Vagrantfile presence)
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx configuration
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with ansible.builtin.package, ansible.builtin.template, and custom configuration management

### Security Considerations

- **Hardcoded credentials**: Redis password "redis_secure_password_123" and PostgreSQL password "fastapi_password" are hardcoded in recipes - migrate to Ansible Vault
- **SSL certificate management**: Self-signed certificates generated via OpenSSL commands - consider Let's Encrypt integration or proper certificate management
- **SSH hardening**: Root login disabled, password authentication disabled - preserve these security configurations
- **Firewall configuration**: UFW rules for SSH, HTTP, HTTPS - maintain equivalent iptables/firewalld rules
- **Fail2ban integration**: SSH protection via fail2ban - preserve jail configurations
- **Sysctl security tuning**: Kernel parameter hardening - maintain security.conf template content
- **Credential patterns per module**:
  - cache: Redis requirepass authentication (1 hardcoded password)
  - fastapi-tutorial: PostgreSQL user password, application environment variables (2 credential types)
  - nginx-multisite: SSL certificate generation, no application credentials

### Technical Challenges

- **Redis configuration patching**: The cache cookbook uses a Ruby block to manually edit Redis config files post-installation - requires custom Ansible lineinfile tasks or template replacement
- **Multi-site SSL certificate generation**: Dynamic certificate creation per site requires Ansible loops and conditional certificate generation
- **PostgreSQL database initialization**: Chef execute blocks for database/user creation need conversion to postgresql_db and postgresql_user modules
- **Systemd service management**: Custom service file creation and daemon-reload orchestration requires proper Ansible handlers
- **Template variable mapping**: Chef ERB templates need conversion to Jinja2 with attribute mapping from Chef node attributes to Ansible variables

### Migration Order

1. **cache** (low risk, standalone service) - Redis and memcached services with minimal external dependencies
2. **nginx-multisite** (moderate complexity) - Web server configuration with security hardening, depends on SSL certificate generation
3. **fastapi-tutorial** (high complexity) - Application deployment with database dependencies, Git integration, and service management

### Assumptions

- Target systems will maintain Ubuntu/CentOS compatibility as specified in cookbook metadata
- Self-signed certificates are acceptable for development environments (production may require CA-signed certificates)
- PostgreSQL service is available via package manager on target systems
- Python 3 and pip are available on target systems for FastAPI application
- Network connectivity allows Git repository cloning for FastAPI tutorial source code
- Systemd is the target service manager (no SysV init support planned)
- UFW firewall is preferred over iptables/firewalld (Ubuntu-centric assumption)
- Redis and memcached will maintain same port configurations (6379 for Redis, default for memcached)
- SSL certificate paths (/etc/ssl/certs, /etc/ssl/private) will remain consistent with current Chef configuration
- Fail2ban jail configurations can be directly ported from ERB templates to Jinja2 templates
- The Ruby-based Redis configuration patching indicates potential compatibility issues with newer Redis versions that may need investigation