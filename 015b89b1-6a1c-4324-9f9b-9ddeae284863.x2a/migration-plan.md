# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with 3 cookbooks managing caching services, a FastAPI application, and a multi-site nginx reverse proxy with SSL termination. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to SSL certificate management, security hardening, and database configuration. Estimated timeline: 3-4 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached installation via community cookbook, Redis with password authentication (redis_secure_password_123), custom Redis configuration patching, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database backend, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning from GitHub, Python virtual environment setup, PostgreSQL database and user creation, environment file with database credentials, systemd service management

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled virtual hosts, security hardening via fail2ban and UFW firewall, and self-signed certificate generation
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site configuration (test.cluster.local, ci.cluster.local, status.cluster.local), SSL certificate auto-generation, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list and node attributes configuration with site-specific settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support specified in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or cloud-agnostic deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules
- **memcached (~> 6.0)**: Replace with community.general.memcached or ansible.builtin.package
- **redisio (~> 7.2.4)**: Replace with community.general.redis or ansible.builtin.package with custom configuration

### Security Considerations

- **Hardcoded Credentials**: Redis password (redis_secure_password_123) and PostgreSQL credentials (fastapi:fastapi_password) are hardcoded in recipes - migrate to Ansible Vault
- **SSL Certificate Management**: Self-signed certificates generated via OpenSSL commands - consider using community.crypto.x509_certificate module
- **SSH Hardening**: Root login disabled, password authentication disabled - migrate using ansible.posix.sysctl and ansible.builtin.lineinfile
- **Firewall Configuration**: UFW rules for HTTP/HTTPS/SSH - migrate using community.general.ufw module
- **Fail2ban Configuration**: Custom jail.local template - migrate using ansible.builtin.template
- **Database Credentials**: PostgreSQL user creation with embedded passwords - migrate to Ansible Vault with postgresql_user module

### Technical Challenges

- **Redis Configuration Patching**: Chef cookbook uses ruby_block to manually edit Redis config file - requires custom Ansible task with ansible.builtin.replace or ansible.builtin.lineinfile
- **Multi-site SSL Management**: Dynamic SSL certificate generation for multiple domains - requires Ansible loops with community.crypto modules
- **Service Dependencies**: Complex service ordering (PostgreSQL before FastAPI, nginx after SSL setup) - use Ansible handlers and task dependencies
- **Git Repository Management**: FastAPI app deployment from GitHub - use ansible.builtin.git module with proper change detection
- **Python Virtual Environment**: Complex pip installation in venv - use ansible.builtin.pip with virtualenv parameters

### Migration Order

1. **cache cookbook** (low risk, standalone caching services)
2. **fastapi-tutorial cookbook** (moderate complexity, database dependencies)
3. **nginx-multisite cookbook** (high complexity, SSL certificates, security hardening, multiple interdependent services)

### Assumptions

- Target systems will maintain Ubuntu/CentOS compatibility as specified in cookbook metadata
- Self-signed certificates are acceptable for the target environment (production may require CA-signed certificates)
- Current hardcoded passwords are acceptable for migration (should be moved to Ansible Vault post-migration)
- PostgreSQL and Redis services will continue to run on the same hosts as the applications
- The GitHub repository for FastAPI tutorial (https://github.com/dibanez/fastapi_tutorial.git) remains accessible
- UFW firewall is the preferred firewall solution (vs iptables or firewalld)
- Systemd is available on target systems for service management
- The three configured sites (test.cluster.local, ci.cluster.local, status.cluster.local) represent the complete site inventory