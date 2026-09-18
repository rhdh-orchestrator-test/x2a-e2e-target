# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with caching, security hardening, and SSL-enabled nginx reverse proxy. The migration involves 3 cookbooks with moderate complexity, requiring approximately 4-6 weeks for complete migration including testing and validation.

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
- Key Features: Git repository cloning, Python venv creation, PostgreSQL database and user provisioning, systemd service configuration, environment file management

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening via fail2ban/UFW, and self-signed certificate generation
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security tuning, self-signed certificate generation

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list and node attributes configuration for all three services
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox (based on Vagrantfile presence)
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules
- **memcached (~> 6.0)**: Replace with community.general.memcached or ansible.builtin.package
- **redisio (~> 7.2.4)**: Replace with community.general.redis or ansible.builtin.package with custom configuration

### Security Considerations

- **Hardcoded credentials**: Redis password "redis_secure_password_123" and PostgreSQL password "fastapi_password" are hardcoded in recipes - migrate to Ansible Vault
- **SSL certificate management**: Self-signed certificates generated via OpenSSL commands - consider Let's Encrypt integration or proper certificate management
- **SSH hardening**: Root login disabled, password authentication disabled - preserve in Ansible with ansible.posix.sshd_config
- **Firewall configuration**: UFW rules for SSH, HTTP, HTTPS - migrate to community.general.ufw module
- **Fail2ban configuration**: Custom jail.local template - migrate to ansible.builtin.template
- **Sysctl security tuning**: Custom security parameters - migrate to ansible.posix.sysctl

### Technical Challenges

- **Redis configuration patching**: The cache cookbook uses a Ruby block to manually edit Redis config files post-installation - this will need to be replaced with proper Jinja2 templating in Ansible
- **Multi-site SSL certificate generation**: Complex loop-based certificate generation for multiple domains will require Ansible loops with conditional certificate creation
- **PostgreSQL database initialization**: Chef execute blocks for database/user creation need migration to community.postgresql modules with proper idempotency
- **Service orchestration**: Multiple interdependent services (nginx, redis, postgresql, fastapi) require careful ordering and dependency management in Ansible playbooks
- **Template migration**: ERB templates need conversion to Jinja2 format with different syntax for variables and conditionals

### Migration Order

1. **cache** (low risk, standalone service) - Redis and memcached have minimal external dependencies
2. **nginx-multisite** (moderate complexity) - Security hardening and SSL setup, but well-contained functionality  
3. **fastapi-tutorial** (high complexity) - Database setup, application deployment, and service dependencies require careful coordination

### Assumptions

- Target systems will maintain the same OS family (Ubuntu/CentOS) as specified in cookbook metadata
- Current hardcoded passwords are acceptable for development environments but will need proper secret management for production
- Self-signed certificates are sufficient for the target environment, or proper CA-signed certificates will be provided separately
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) will remain accessible during migration
- PostgreSQL version compatibility will be maintained between Chef and Ansible deployments
- UFW firewall is the preferred firewall solution for the target environment
- Systemd is available on target systems for service management
- The three-site configuration (test.cluster.local, ci.cluster.local, status.cluster.local) will be preserved in the Ansible implementation