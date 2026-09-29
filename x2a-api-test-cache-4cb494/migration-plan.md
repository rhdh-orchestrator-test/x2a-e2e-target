# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with 3 cookbooks managing web services, caching infrastructure, and a FastAPI application. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to multi-service dependencies and security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx reverse proxy with SSL-enabled multi-site hosting, security hardening via fail2ban/UFW, and self-signed certificate generation for development environments
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multiple SSL virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local), fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security tuning, self-signed certificate generation

**cache**:
- Description: Caching services configuration providing both Memcached and Redis with authentication and custom Redis configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached service, Redis with password authentication (redis_secure_password_123), custom Redis configuration patching via ruby_block, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database backend, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning from GitHub, Python virtual environment setup, PostgreSQL database and user creation, systemd service management, environment configuration file

### Infrastructure Files

- `Berksfile`: Chef cookbook dependency management with external dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list configuration and node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning (requires review for Vagrant-specific configurations)
- `vagrant-provision.sh`: Shell provisioning script for Vagrant environment setup

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support specified in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom Redis configuration tasks
- **Chef Solo**: Replace with Ansible playbook execution via ansible-playbook command

### Security Considerations

- **Hardcoded credentials**: Redis password (redis_secure_password_123) and PostgreSQL password (fastapi_password) are hardcoded in recipes - migrate to Ansible Vault
- **SSL certificate management**: Self-signed certificates generated via OpenSSL commands - consider Let's Encrypt integration or proper certificate management
- **SSH hardening**: Root login disabled, password authentication disabled - preserve these security configurations
- **Firewall configuration**: UFW rules for SSH, HTTP, HTTPS - migrate to ansible.posix.ufw module
- **Fail2ban configuration**: Custom jail.local template - migrate template to Jinja2 format
- **Sysctl security tuning**: Custom kernel parameter hardening - migrate to ansible.posix.sysctl module

### Technical Challenges

- **Ruby block workarounds**: The cache cookbook contains a Ruby block hack to fix Redis configuration files - this custom logic needs to be reimplemented using Ansible's lineinfile or replace modules
- **Multi-service coordination**: The nginx-multisite cookbook orchestrates multiple services (nginx, fail2ban, ufw, ssh) - ensure proper task ordering and handler notifications in Ansible
- **Template migration**: ERB templates (.erb) need conversion to Jinja2 (.j2) format with syntax adjustments
- **Git repository management**: FastAPI cookbook clones from GitHub - ensure proper Git module usage and repository access in target environment
- **PostgreSQL user/database creation**: SQL commands executed via shell - migrate to community.postgresql.* modules for idempotent database management

### Migration Order

1. **cache** (low risk, standalone service with clear dependencies)
2. **fastapi-tutorial** (moderate complexity, database dependencies but isolated application)
3. **nginx-multisite** (high complexity, multiple security configurations and service dependencies)

### Assumptions

- Target environments have internet access for package installation and Git repository cloning
- PostgreSQL service is available or can be installed on target systems
- SSL certificates are acceptable as self-signed for development environments (production may require proper CA-signed certificates)
- The Ruby block hack in the Redis configuration indicates potential compatibility issues with the redisio cookbook version that may not exist in native Redis packages
- Vagrant development environment setup will be replaced with equivalent Ansible testing methodology
- Current Chef Solo execution model will be replaced with standard Ansible playbook execution
- Network connectivity exists between services (nginx proxy to FastAPI application on port 8000)
- File permissions and ownership requirements remain consistent across Chef and Ansible implementations