# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing web services, caching infrastructure, and a FastAPI application. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to SSL configuration, security hardening, and database setup. Estimated timeline: 3-4 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx web server with SSL-enabled multi-site hosting, security hardening via fail2ban/UFW, and comprehensive HTTP security headers
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: SSL/TLS termination with strong cipher suites, HSTS headers, fail2ban intrusion prevention, UFW firewall configuration, SSH hardening, sysctl security tuning, custom site templates with CSP headers

**cache**:
- Description: Caching infrastructure with Redis and Memcached services, including Redis authentication and custom configuration management
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis 6379 with password authentication, Memcached service, custom Redis configuration file manipulation, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application with PostgreSQL database backend, systemd service management, and virtual environment setup
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Python 3 virtual environment, Git repository cloning, PostgreSQL database and user creation, systemd service configuration, environment variable management

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list configuration and attribute overrides for site domains and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be VM-based deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks
- **PostgreSQL**: Replace with community.postgresql.* collection modules
- **Python/pip packages**: Replace with ansible.builtin.pip module

### Security Considerations

- **Hardcoded credentials**: Redis password "redis_secure_password_123" and PostgreSQL password "fastapi_password" are hardcoded in recipes - migrate to Ansible Vault
- **SSL certificate management**: SSL certificates and private keys referenced in templates need secure deployment via Ansible Vault
- **SSH security configuration**: Root login disable and password authentication disable need careful migration to avoid lockout
- **Firewall rules**: UFW configuration requires proper ordering to avoid connection loss during deployment
- **Database credentials**: PostgreSQL user creation with embedded passwords needs Vault integration
- **Environment files**: FastAPI .env file contains database connection strings with credentials

### Technical Challenges

- **Redis configuration manipulation**: Chef cookbook uses Ruby block to modify Redis config file post-installation - requires custom Ansible lineinfile tasks or template replacement
- **SSL certificate deployment**: Site templates expect SSL certificates to be present - migration needs certificate provisioning strategy
- **Service dependencies**: FastAPI service depends on PostgreSQL being ready - requires proper Ansible task ordering and handlers
- **Multi-site nginx configuration**: Dynamic site generation from attributes needs Ansible template loops and proper site enabling/disabling
- **Chef Solo to Ansible conversion**: Solo.json attribute structure needs mapping to Ansible group_vars/host_vars

### Migration Order

1. **cache cookbook** (low risk, standalone services with clear dependencies)
2. **fastapi-tutorial cookbook** (moderate complexity, database setup and application deployment)
3. **nginx-multisite cookbook** (highest complexity, SSL configuration, security hardening, and multi-site management)

### Assumptions

- SSL certificates are manually deployed or obtained via external process (not managed by Chef cookbooks)
- Target environments have internet access for package installation and Git repository cloning
- PostgreSQL service configuration beyond basic setup is handled externally
- Firewall rules assume standard SSH (port 22), HTTP (port 80), and HTTPS (port 443) access patterns
- Redis and Memcached default configurations are sufficient beyond the specific Redis authentication and logging customizations
- FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and compatible
- Development environment uses Vagrant, but production deployment method is not specified in the current configuration