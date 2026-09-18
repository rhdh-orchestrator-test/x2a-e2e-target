# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing caching services, a FastAPI application, and a multi-site nginx reverse proxy with SSL termination. The migration involves converting Chef cookbooks to Ansible playbooks and roles, addressing external dependencies, and maintaining security configurations including fail2ban, UFW firewall, and SSL certificate management.

**Estimated Timeline**: 4-6 weeks for complete migration
**Complexity**: Medium - straightforward service configurations with some security hardening
**Team Coordination**: Requires coordination between application, infrastructure, and security teams

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **cache**:
    - Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Memcached service, Redis with password authentication (redis_secure_password_123), custom Redis configuration patching, log directory management

- **fastapi-tutorial**:
    - Description: FastAPI Python web application deployment with PostgreSQL database backend, virtual environment management, and systemd service configuration
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service management, environment configuration file

- **nginx-multisite**:
    - Description: Nginx reverse proxy with multiple SSL-enabled virtual hosts, security hardening, and self-signed certificate generation
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration (test.cluster.local, ci.cluster.local, status.cluster.local), SSL certificate generation, fail2ban integration, UFW firewall configuration, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list and node attributes configuration with site-specific settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support specified in metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (based on Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks

### Security Considerations

- **Hardcoded Credentials**: Redis password (redis_secure_password_123) and PostgreSQL credentials (fastapi_password) are hardcoded in recipes - migrate to Ansible Vault
- **SSL Certificate Management**: Self-signed certificate generation for development environments - consider Let's Encrypt integration for production
- **SSH Hardening**: Root login disabled, password authentication disabled - maintain these security settings
- **Firewall Configuration**: UFW rules for SSH, HTTP, HTTPS - preserve firewall rules during migration
- **Fail2ban Integration**: Intrusion prevention system configuration - ensure fail2ban rules are maintained
- **Sysctl Security Tuning**: Kernel parameter hardening - preserve security-focused sysctl settings

### Technical Challenges

- **Redis Configuration Patching**: The cache cookbook includes a Ruby block that manually edits Redis configuration files to remove specific directives - this will need to be replicated using Ansible's lineinfile or replace modules
- **Multi-site SSL Management**: Dynamic SSL certificate generation for multiple sites requires careful templating and certificate lifecycle management in Ansible
- **Service Dependencies**: FastAPI application depends on PostgreSQL being available - ensure proper task ordering and service dependency management
- **File Permissions**: SSL private keys require specific ownership (root:ssl-cert) and permissions (640) - maintain security-focused file permissions

### Migration Order

1. **cache** (low risk, foundational service) - Redis and memcached are standalone services with minimal dependencies
2. **nginx-multisite** (moderate complexity) - Web server configuration with security hardening, depends on SSL certificate generation
3. **fastapi-tutorial** (high complexity) - Application deployment with database dependencies, requires coordination with application team

### Assumptions

- Development environment uses self-signed certificates, production may require different certificate management approach
- Current hardcoded passwords are acceptable for development but will need proper secret management for production
- UFW firewall rules are sufficient for the target environment security requirements
- PostgreSQL database initialization scripts are idempotent and can be safely re-run
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and stable
- Target systems have internet access for package installation and git repository cloning
- The Ruby-based Redis configuration patching is a temporary workaround that can be replaced with proper configuration management
- Site-specific HTML files (test, ci, status) are static content that doesn't require dynamic generation