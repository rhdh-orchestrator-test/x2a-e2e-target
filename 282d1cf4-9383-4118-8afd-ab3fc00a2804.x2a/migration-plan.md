# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with 3 cookbooks managing caching services, a FastAPI application, and a multi-site nginx reverse proxy with SSL termination. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to SSL certificate management, security hardening, and database configuration. Estimated timeline: 3-4 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached installation, Redis with password authentication (redis_secure_password_123), custom Redis configuration patching via ruby_block, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database backend, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning from GitHub, Python virtual environment setup, PostgreSQL database and user creation, systemd service management, environment configuration file

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled virtual hosts, security hardening via fail2ban and UFW firewall, and self-signed certificate generation
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site configuration (test.cluster.local, ci.cluster.local, status.cluster.local), SSL certificate generation, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list configuration and node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file for cookbook and data bag paths
- `Vagrantfile`: Development environment provisioning with Vagrant
- `vagrant-provision.sh`: Shell script for Vagrant VM provisioning

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or development environment focused

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks

### Security Considerations

- **Hardcoded credentials**: Redis password (redis_secure_password_123) and PostgreSQL credentials (fastapi:fastapi_password) are embedded in recipes - migrate to Ansible Vault
- **SSL certificate management**: Self-signed certificates generated via OpenSSL commands - consider using community.crypto.x509_certificate module
- **SSH hardening**: Root login disabled, password authentication disabled - migrate to ansible.posix.sshd_config module
- **Firewall configuration**: UFW rules for HTTP/HTTPS/SSH - migrate to community.general.ufw module
- **Fail2ban configuration**: Custom jail.local template - migrate to community.general.fail2ban module
- **Credential types per module**:
  - cache: Redis authentication password
  - fastapi-tutorial: PostgreSQL database credentials, no SSL certificates
  - nginx-multisite: SSL private keys, no database credentials

### Technical Challenges

- **Ruby block workarounds**: The cache cookbook uses a ruby_block to patch Redis configuration files post-installation - this will need to be replaced with Ansible lineinfile or template modules
- **Complex SSL certificate generation**: Multi-site SSL certificate creation with proper file permissions and ownership requires careful migration to Ansible crypto modules
- **Service dependency management**: PostgreSQL must be running before database creation, nginx must reload after SSL certificate generation - use Ansible handlers and task dependencies
- **Git repository cloning**: FastAPI tutorial clones from GitHub - ensure proper SSH key or token management in Ansible
- **Multi-platform support**: Cookbooks support both Ubuntu and CentOS - ensure Ansible playbooks handle package manager differences

### Migration Order

1. **cache** (low risk, high value) - Simple service installation with well-defined configuration
2. **fastapi-tutorial** (moderate complexity) - Application deployment with database dependencies but straightforward systemd service
3. **nginx-multisite** (high complexity, dependencies) - Complex multi-site configuration with SSL, security hardening, and firewall rules

### Assumptions

- SSL certificates are self-signed for development/testing purposes - production deployment may require Let's Encrypt or CA-signed certificates
- PostgreSQL and Redis run on the same host as the applications - distributed deployment may require connection string modifications
- UFW firewall rules are sufficient for the security model - enterprise environments may require additional iptables rules
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and the main branch is stable
- Current Chef Solo deployment model will be replaced with Ansible playbook execution - inventory management and host targeting strategies need definition
- Development environment uses Vagrant with local cookbooks - production deployment method and cookbook distribution mechanism unclear
- No external secrets management system is currently in use - migration to Ansible Vault assumes this is acceptable for the target environment