# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing web services, caching infrastructure, and a FastAPI application. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to security configurations, SSL certificate management, and database setup. Estimated timeline: 3-4 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached installation, Redis with password authentication, custom Redis configuration patching, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Python 3 virtual environment, Git repository cloning, PostgreSQL database and user creation, systemd service management, environment configuration

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled virtual hosts, security hardening, and fail2ban integration
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, self-signed certificate generation, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef cookbook dependency management - defines external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo configuration with run list and node attributes - contains site configurations, SSL paths, and security settings
- `solo.rb`: Chef Solo execution configuration
- `Vagrantfile`: Development environment provisioning for testing
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata.rb supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (based on Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be generic Linux deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx configuration
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with ansible.builtin.package, custom Redis configuration templates, and service management

### Security Considerations

- **Hardcoded credentials**: Redis password "redis_secure_password_123" and PostgreSQL password "fastapi_password" are hardcoded in recipes - migrate to Ansible Vault
- **SSL certificate management**: Self-signed certificate generation with OpenSSL commands - consider using ansible.builtin.openssl_certificate module or Let's Encrypt integration
- **SSH hardening**: Root login disable and password authentication disable via sed commands - migrate to ansible.builtin.lineinfile module
- **Firewall configuration**: UFW rules for SSH, HTTP, HTTPS - migrate to community.general.ufw module
- **Fail2ban configuration**: Custom jail.local template - migrate to ansible.builtin.template module
- **Sysctl security tuning**: Custom security.conf template - migrate to ansible.posix.sysctl module
- **Credential types identified**: Database passwords (2), Redis authentication (1), SSL certificates (3 self-signed)

### Technical Challenges

- **Redis configuration patching**: Chef cookbook uses Ruby block to manually edit Redis config file with regex replacements - requires custom Ansible task or improved template approach
- **Multi-site SSL management**: Dynamic SSL certificate generation for multiple sites requires loop-based certificate creation in Ansible
- **Database initialization**: PostgreSQL user and database creation uses shell commands with error handling - migrate to community.postgresql modules
- **Service dependencies**: Complex service ordering (PostgreSQL before FastAPI, nginx after SSL certificates) requires careful Ansible task ordering and handlers
- **File permissions and ownership**: Multiple file permission settings (ssl-cert group, www-data ownership) need careful mapping to Ansible file module

### Migration Order

1. **cache** (low risk, high value) - Straightforward package installation and service configuration, minimal dependencies
2. **nginx-multisite** (moderate complexity) - SSL and security configurations are complex but well-contained, no external service dependencies
3. **fastapi-tutorial** (high complexity, dependencies) - Requires database setup, application deployment, and service integration - should be migrated last

### Assumptions

- Target systems will have internet access for package installation and Git repository cloning
- PostgreSQL service will be managed locally rather than using external database servers
- Self-signed certificates are acceptable for the target environment (development/testing)
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) will remain accessible
- UFW firewall is the preferred firewall solution for the target Ubuntu systems
- The ssl-cert group exists or can be created on target systems
- Systemd is available for service management on target systems
- The current hardcoded passwords are acceptable for migration (should be moved to Ansible Vault)
- The custom Redis configuration fixes in the Ruby block are still necessary for the target Redis version