# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing web services, caching infrastructure, and a FastAPI application. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to security configurations, SSL certificate management, and database setup. Estimated timeline: 3-4 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication, memcached integration, custom Redis configuration patching, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment setup, and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment, PostgreSQL database and user creation, systemd service configuration, environment file management

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

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (based on Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be VM-based deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx configuration
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with ansible.builtin.package, custom Redis configuration templates, and service management

### Security Considerations

- **Hardcoded credentials**: Redis password "redis_secure_password_123" and PostgreSQL password "fastapi_password" are hardcoded in recipes - migrate to Ansible Vault
- **SSL certificate management**: Self-signed certificate generation with OpenSSL commands - consider using ansible.builtin.openssl_certificate module
- **SSH hardening**: Root login disable and password authentication disable via sed commands - use ansible.builtin.lineinfile module
- **Firewall configuration**: UFW rules for HTTP/HTTPS/SSH - use community.general.ufw module
- **Fail2ban configuration**: Template-based jail configuration - use ansible.builtin.template module
- **Sysctl security tuning**: Custom kernel parameter configuration - use ansible.posix.sysctl module
- **Credential types identified**: Database passwords (2), Redis authentication (1), SSL certificate paths

### Technical Challenges

- **Redis configuration patching**: Chef uses a Ruby block to manually edit Redis config file with regex replacements - requires custom Ansible task or template approach
- **Multi-site SSL certificate generation**: Dynamic certificate creation per site requires loop-based Ansible tasks with conditional certificate generation
- **Database initialization**: PostgreSQL user and database creation uses shell commands with error handling - needs idempotent Ansible postgresql modules
- **Service dependencies**: FastAPI service depends on PostgreSQL being ready - requires proper Ansible handler ordering and service dependencies
- **Template variable mapping**: Chef attributes need to be converted to Ansible variables with proper scoping

### Migration Order

1. **cache** (low risk, high value) - Straightforward package installation and service configuration, minimal external dependencies
2. **nginx-multisite** (moderate complexity) - SSL and security configurations require careful testing, but well-defined scope
3. **fastapi-tutorial** (high complexity, dependencies) - Application deployment with database setup, Git operations, and service management dependencies

### Assumptions

- Target systems will have internet access for package installation and Git repository cloning
- PostgreSQL will be installed locally rather than using external database service
- Self-signed certificates are acceptable for the target environment (development/testing)
- UFW firewall is the preferred firewall solution for the target Ubuntu systems
- Systemd is available on target systems for service management
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) will remain accessible
- Current Chef cookbook versions and external dependencies are compatible with target system package versions
- SSL certificate paths (/etc/ssl/certs and /etc/ssl/private) are standard and acceptable for target environment
- Redis and memcached will continue to run on default ports (6379 and 11211 respectively)
- The nginx sites configuration assumes local DNS resolution for *.cluster.local domains