# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing caching services, a FastAPI application, and a multi-site nginx reverse proxy with SSL termination. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to security configurations, SSL certificate management, and database setup. Estimated timeline: 3-4 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached installation, Redis with password authentication (redis_secure_password_123), custom Redis configuration patching, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database backend, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Python 3 virtual environment, Git repository cloning, PostgreSQL database and user creation, systemd service management, environment configuration file

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled virtual hosts, security hardening via fail2ban and UFW firewall, and self-signed certificate generation
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site configuration (test.cluster.local, ci.cluster.local, status.cluster.local), SSL certificate generation, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef cookbook dependency management with external dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list configuration and node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or cloud-agnostic deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and community.general.memcached module
- **redisio (~> 7.2.4)**: Replace with community.general.redis module and custom configuration management

### Security Considerations

- **Hardcoded Credentials**: Redis password (redis_secure_password_123) and PostgreSQL credentials (fastapi:fastapi_password) are hardcoded in recipes - migrate to Ansible Vault
- **SSL Certificate Management**: Self-signed certificates generated via OpenSSL commands - consider using community.crypto.x509_certificate module
- **SSH Hardening**: Root login disabled, password authentication disabled - migrate using ansible.posix.sshd_config module
- **Firewall Configuration**: UFW rules for SSH, HTTP, HTTPS - migrate using community.general.ufw module
- **Fail2ban Configuration**: Custom jail.local template - migrate using community.general.ini_file module
- **Database Credentials**: PostgreSQL user and database creation with embedded passwords - migrate to Ansible Vault
- **Environment Files**: .env file with database connection string containing password - secure with Ansible Vault

### Technical Challenges

- **Redis Configuration Patching**: The cache cookbook includes a Ruby block that manually edits Redis configuration files to remove specific directives - this will need to be reimplemented using Ansible's lineinfile or replace modules
- **Multi-site SSL Management**: Dynamic SSL certificate generation for multiple sites based on node attributes - will require Ansible loops and conditional logic
- **Service Dependencies**: Complex service ordering (PostgreSQL before FastAPI, nginx after SSL certificates) - use Ansible handlers and proper task ordering
- **Template Migration**: ERB templates need conversion to Jinja2 format for nginx.conf, security.conf, fail2ban.jail.local, site.conf, and sysctl-security.conf
- **File Resource Management**: Static HTML files for different sites need to be managed through Ansible file modules

### Migration Order

1. **cache** (low risk, standalone service with clear dependencies)
2. **nginx-multisite** (moderate complexity, security configurations require careful testing)
3. **fastapi-tutorial** (highest complexity, database dependencies and application deployment)

### Assumptions

- Target systems will have similar package availability (nginx, postgresql, python3, etc.) as the current Ubuntu/CentOS environments
- SSL certificates are currently self-signed for development - production deployment may require different certificate management approach
- The Redis configuration patching hack suggests potential compatibility issues that may need investigation in the target environment
- Database initialization is idempotent in the current Chef implementation - Ansible equivalent will need similar idempotency checks
- Static HTML files in the cookbook files directory are simple placeholder content and not critical application assets
- The Vagrant development environment will be replaced with an equivalent Ansible-based development setup
- Network connectivity and firewall rules are appropriate for the target environment
- Service user accounts (www-data, redis, postgres) exist or can be created on target systems