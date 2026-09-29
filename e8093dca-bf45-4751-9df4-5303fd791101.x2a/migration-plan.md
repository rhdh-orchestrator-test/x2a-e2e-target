# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing web services, caching infrastructure, and a Python FastAPI application. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to security configurations, SSL certificate management, and database setup. Estimated timeline: 3-4 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication, log directory setup, and configuration file manipulation
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis password authentication, memcached integration, Redis configuration file patching via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment setup, and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment, PostgreSQL database and user creation, systemd service configuration, environment file management

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled virtual hosts, security hardening via fail2ban and UFW firewall, and self-signed certificate generation
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site configuration, SSL certificate generation, fail2ban integration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef cookbook dependency management with external dependencies from Chef Supermarket
- `solo.json`: Chef Solo configuration with run list and node attributes for site configuration and security settings
- `solo.rb`: Chef Solo execution configuration
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis or custom Redis configuration tasks
- **nginx (~> 12.0)**: Replace with nginxinc.nginx collection or ansible.builtin.package with custom configuration

### Security Considerations

- **Hardcoded credentials**: Redis password "redis_secure_password_123" and PostgreSQL password "fastapi_password" are hardcoded in recipes - migrate to Ansible Vault
- **SSL certificate management**: Self-signed certificates generated via OpenSSL commands - consider using community.crypto.x509_certificate module
- **SSH hardening**: Root login disabled, password authentication disabled - migrate using ansible.posix.sshd_config module
- **Firewall configuration**: UFW rules for HTTP/HTTPS/SSH - migrate using community.general.ufw module
- **Fail2ban integration**: Jail configuration via template - migrate using ansible.builtin.template module
- **Sysctl security tuning**: Kernel parameter hardening - migrate using ansible.posix.sysctl module

### Technical Challenges

- **Ruby block configuration patching**: The cache cookbook uses ruby_block to modify Redis configuration files post-installation - requires conversion to Ansible lineinfile or replace modules
- **Complex service dependencies**: FastAPI service depends on PostgreSQL being ready - implement proper service ordering with ansible.builtin.systemd and wait_for conditions
- **Multi-site SSL certificate generation**: Dynamic certificate creation per site requires Ansible loops with community.crypto modules
- **Template variable mapping**: Chef ERB templates need conversion to Jinja2 with attribute mapping from Chef node attributes to Ansible variables

### Migration Order

1. **cache** (low risk, foundational service) - Redis and memcached are standalone services with minimal dependencies
2. **nginx-multisite** (moderate complexity) - Web server configuration with security hardening, depends on SSL certificate generation
3. **fastapi-tutorial** (high complexity) - Application deployment with database dependencies, requires coordination with nginx for reverse proxy setup

### Assumptions

- Chef Solo execution model suggests single-node deployments - Ansible playbooks will target individual hosts rather than orchestrating multi-node clusters
- Development environment uses Vagrant - production deployment method not specified in repository
- SSL certificates are self-signed for development - production may require Let's Encrypt or CA-signed certificates
- Database credentials are for development use - production will require proper secret management
- Ubuntu/Debian package management assumed based on apt package names in recipes - CentOS support may need additional testing
- Network configuration assumes standard HTTP/HTTPS ports - custom port configurations not evident in current setup
- Service management uses systemd - older init systems not considered in current cookbook implementations