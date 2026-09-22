# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with caching, security hardening, and SSL-enabled nginx reverse proxy. The migration involves 3 cookbooks with moderate complexity, requiring approximately 4-6 weeks for complete migration including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with Memcached and Redis, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached service, Redis with password authentication (redis_secure_password_123), custom Redis configuration cleanup, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database backend and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Python 3 virtual environment, Git repository cloning, PostgreSQL database and user creation, systemd service configuration, environment variable management

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled virtual hosts, security hardening, and firewall configuration
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, self-signed certificate generation, fail2ban integration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run configuration with site-specific attributes and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox (based on Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be local/on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom Redis configuration tasks

### Security Considerations

- **Hardcoded credentials**: Redis password (redis_secure_password_123) and PostgreSQL credentials (fastapi_password) are embedded in recipes - migrate to Ansible Vault
- **SSL certificate management**: Self-signed certificates generated via OpenSSL commands - consider Let's Encrypt integration or proper certificate management
- **SSH hardening**: Root login disabled, password authentication disabled - maintain these security configurations
- **Firewall rules**: UFW configuration for HTTP/HTTPS/SSH - migrate to ansible.posix.ufw module
- **fail2ban configuration**: Nginx protection rules - migrate to community.general.fail2ban module
- **Credential patterns per module**:
  - cache: Redis authentication password (1 hardcoded credential)
  - fastapi-tutorial: PostgreSQL user password, database connection string (2 hardcoded credentials)
  - nginx-multisite: SSL certificate generation (certificate management, not credentials per se)

### Technical Challenges

- **Redis configuration cleanup**: The cache cookbook includes a Ruby block hack to fix Redis configuration - this custom logic needs careful translation to Ansible tasks
- **Multi-site SSL management**: Dynamic SSL certificate generation and site configuration requires Jinja2 templating and loop constructs
- **Service dependencies**: PostgreSQL must be running before FastAPI application starts - ensure proper task ordering and handlers
- **File permissions**: SSL certificates require specific ownership (root:ssl-cert) and permissions (640) - maintain security model
- **Template complexity**: Nginx configuration templates need conversion from ERB to Jinja2 format

### Migration Order

1. **cache** (low risk, high value) - Straightforward service installation with known configuration patterns
2. **fastapi-tutorial** (moderate complexity) - Application deployment with database dependencies but well-defined workflow
3. **nginx-multisite** (high complexity, dependencies) - Complex multi-site configuration with SSL, security hardening, and firewall rules

### Assumptions

- Target systems will maintain Ubuntu/CentOS compatibility as specified in cookbook metadata
- Current Redis password and PostgreSQL credentials are acceptable for migration to Ansible Vault (not production-ready)
- Self-signed certificates are acceptable for the target environment (development/testing)
- The Ruby block hack for Redis configuration cleanup addresses a specific version compatibility issue that may not exist in target Redis versions
- UFW firewall is the preferred firewall solution for the target environment
- Systemd is available on target systems for service management
- The FastAPI tutorial repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and compatible
- Current site names (test.cluster.local, ci.cluster.local, status.cluster.local) will be maintained in the Ansible implementation
- The /var/www vs /opt/server document root discrepancy between attributes and solo.json will be resolved during migration