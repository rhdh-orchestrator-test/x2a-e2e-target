# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing caching services, a FastAPI application, and a multi-site nginx reverse proxy with security hardening. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to security configurations, SSL certificate management, and database setup. Estimated timeline: 3-4 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis 6379, including authentication, logging, and configuration file manipulation
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis authentication (requirepass), custom log directory, configuration file patching via ruby_block, memcached integration

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment setup, and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python venv creation, PostgreSQL database and user provisioning, systemd service configuration, environment file management

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening via fail2ban/UFW, and self-signed certificate generation
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site configuration (test/ci/status.cluster.local), SSL certificate generation, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo configuration with run_list and node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo execution configuration
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox (based on Vagrantfile presence)
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom configuration templates

### Security Considerations

- **Hardcoded credentials**: Redis password 'redis_secure_password_123' and PostgreSQL password 'fastapi_password' are hardcoded in recipes - migrate to Ansible Vault
- **SSL certificate management**: Self-signed certificates generated via OpenSSL commands - consider using community.crypto.x509_certificate module
- **SSH hardening**: Root login disabled, password authentication disabled - migrate using ansible.posix.sshd_config module
- **Firewall configuration**: UFW rules for SSH/HTTP/HTTPS - migrate using community.general.ufw module
- **Fail2ban configuration**: Custom jail.local template - migrate using community.general.fail2ban module
- **Sysctl security tuning**: Custom kernel parameters - migrate using ansible.posix.sysctl module
- **Credential types per module**:
  - cache: Redis authentication password
  - fastapi-tutorial: PostgreSQL database credentials, no encrypted data bags detected
  - nginx-multisite: SSL certificate generation, no vault usage detected

### Technical Challenges

- **Ruby block configuration patching**: The cache cookbook uses ruby_block to modify Redis config files post-installation - requires custom Ansible tasks with lineinfile or replace modules
- **Complex nginx site management**: Dynamic site creation with SSL certificates requires careful template management and certificate generation coordination
- **PostgreSQL database initialization**: Database and user creation commands need conversion to postgresql_* modules with proper idempotency
- **Service dependency ordering**: FastAPI service depends on PostgreSQL, nginx depends on SSL certificates - requires proper task ordering and handlers
- **Template variable mapping**: Chef ERB templates need conversion to Jinja2 with attribute mapping from Chef node attributes to Ansible variables

### Migration Order

1. **cache** (low risk, high value) - Straightforward service installation with configuration templates, minimal external dependencies
2. **nginx-multisite** (moderate complexity) - Security hardening and SSL management, but well-contained functionality
3. **fastapi-tutorial** (high complexity, dependencies) - Application deployment with database setup, Git operations, and systemd service management

### Assumptions

- Target systems will maintain the same OS family (Ubuntu/CentOS) as specified in cookbook metadata
- Self-signed certificates are acceptable for the target environment (production may require CA-signed certificates)
- PostgreSQL and Redis will be installed locally rather than using external managed services
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and compatible
- Current hardcoded passwords are acceptable for development but will need proper secret management in production
- UFW firewall is the preferred firewall solution (vs iptables or firewalld)
- The three subdomain sites (test/ci/status.cluster.local) will maintain the same naming convention
- Systemd is available on target systems for service management
- The ruby_block configuration patching in the cache cookbook indicates potential Redis configuration issues that may need investigation