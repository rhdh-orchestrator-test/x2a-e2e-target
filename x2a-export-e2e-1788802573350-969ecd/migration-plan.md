# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with nginx reverse proxy, caching services (Redis/Memcached), and a FastAPI application with PostgreSQL backend. The migration involves 3 custom cookbooks with moderate complexity, requiring approximately 4-6 weeks for complete migration including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **cache**:
    - Description: Caching services configuration with Redis authentication and Memcached setup, including custom Redis configuration fixes and log directory management
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with requirepass authentication, Memcached integration, custom Redis config file manipulation, log directory creation

- **fastapi-tutorial**:
    - Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment setup, and systemd service management
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository cloning, Python venv creation, PostgreSQL database and user provisioning, systemd service configuration, environment file management

- **nginx-multisite**:
    - Description: Nginx reverse proxy with SSL-enabled multi-domain hosting, security hardening via fail2ban/UFW, and self-signed certificate generation
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-domain SSL configuration, fail2ban integration, UFW firewall rules, SSH hardening, sysctl security tuning, self-signed certificate generation

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4) and local cookbook paths
- `solo.json`: Chef Solo run list configuration and node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file for cookbook and data bag paths
- `Vagrantfile`: Development environment provisioning with Chef Solo integration
- `vagrant-provision.sh`: Shell script for Vagrant VM provisioning automation

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be local development/on-premises deployment

## Migration Approach

### Key Dependencies to Address
- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom configuration tasks
- **Chef Solo**: Replace with Ansible playbooks and inventory management

### Security Considerations
- **Hardcoded credentials**: Redis password ('redis_secure_password_123') and PostgreSQL credentials ('fastapi_password') are embedded in recipes - migrate to Ansible Vault
- **SSL certificate management**: Self-signed certificates generated via OpenSSL commands - consider Let's Encrypt integration with community.crypto collection
- **SSH hardening**: Root login disable and password authentication disable configured via sed commands - migrate to ansible.posix.sshd_config module
- **Firewall configuration**: UFW rules managed via shell commands - migrate to community.general.ufw module
- **Fail2ban configuration**: Template-based jail configuration - migrate to community.general.ini_file or template modules
- **File permissions**: SSL private keys with specific group ownership (ssl-cert) - ensure proper Ansible file module configuration

### Technical Challenges
- **Custom Redis configuration manipulation**: Chef ruby_block performs regex-based config file editing - requires careful translation to Ansible lineinfile or replace modules
- **Multi-domain SSL certificate generation**: Loop-based certificate creation for multiple sites - implement with Ansible loops and community.crypto.x509_certificate
- **Service dependency management**: PostgreSQL must be running before database user creation - use Ansible handlers and service state management
- **Git repository synchronization**: Chef git resource with revision tracking - migrate to ansible.builtin.git module with version pinning
- **Python virtual environment management**: Custom pip installation within venv - use ansible.builtin.pip with virtualenv parameters

### Migration Order
1. **cache** (low risk, foundational service) - Redis and Memcached are well-supported in Ansible with standard modules
2. **nginx-multisite** (moderate complexity) - Security hardening and SSL configuration require careful testing but use standard Ansible modules
3. **fastapi-tutorial** (high complexity) - Application deployment with database dependencies and service management requires comprehensive integration testing

### Assumptions
- Target systems will maintain the same OS distributions (Ubuntu 18.04+, CentOS 7+) as specified in cookbook metadata
- Self-signed certificates are acceptable for the target environment (production deployments may require CA-signed certificates)
- PostgreSQL and Redis passwords can be migrated to Ansible Vault without changing the actual credential values
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and the 'main' branch is stable
- UFW firewall is the preferred firewall solution for the target environment
- Systemd is available on target systems for service management
- The ssl-cert group exists or can be created on target systems for SSL private key access
- Network connectivity allows access to external package repositories and the FastAPI tutorial Git repository
- The current Chef Solo workflow can be replaced with Ansible playbook execution without requiring Chef Server infrastructure