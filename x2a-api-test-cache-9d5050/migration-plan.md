# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with caching, security hardening, and SSL-enabled nginx reverse proxy. The migration involves 3 cookbooks with moderate complexity, estimated timeline of 3-4 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis authentication, includes Redis log directory setup and configuration file patching
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached integration, Redis with password authentication (redis_secure_password_123), custom Redis configuration patching via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python venv creation, PostgreSQL database and user provisioning, systemd service management, environment file configuration

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening via fail2ban/UFW, and self-signed certificate generation
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security tuning, self-signed certificate generation

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list configuration and node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support specified in metadata.rb files)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or cloud-agnostic deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks

### Security Considerations

- **Hardcoded Credentials**: Redis password (redis_secure_password_123) and PostgreSQL credentials (fastapi:fastapi_password) are hardcoded in recipes - migrate to Ansible Vault
- **SSL Certificate Management**: Self-signed certificates generated via OpenSSL commands - consider using community.crypto.x509_certificate module
- **SSH Hardening**: Root login disabled, password authentication disabled - migrate using ansible.posix.sysctl and lineinfile modules
- **Firewall Configuration**: UFW rules for SSH, HTTP, HTTPS - migrate using community.general.ufw module
- **Fail2ban Configuration**: Custom jail.local template - migrate using ansible.builtin.template module
- **Credential Types per Module**:
  - cache: Redis authentication password
  - fastapi-tutorial: PostgreSQL database credentials, application environment variables
  - nginx-multisite: SSL certificate generation (self-signed)

### Technical Challenges

- **Ruby Block Logic**: The cache cookbook uses a ruby_block to patch Redis configuration files with regex replacements - will need custom Ansible tasks with lineinfile or replace modules
- **Multi-Site SSL Management**: Dynamic SSL certificate generation for multiple domains requires loop-based certificate creation in Ansible
- **Service Dependencies**: PostgreSQL must be running before database/user creation, nginx must reload after configuration changes - use handlers and task dependencies
- **Git Repository Cloning**: FastAPI app deployment from GitHub requires git module with proper authentication handling
- **Python Virtual Environment**: venv creation and pip installation requires ansible.builtin.pip module with virtualenv parameters

### Migration Order

1. **nginx-multisite** (foundational infrastructure, security baseline)
2. **cache** (moderate complexity, fewer external dependencies)
3. **fastapi-tutorial** (highest complexity, depends on database and application stack)

### Assumptions

- Target systems will have internet access for package installation and git repository cloning
- SSL certificates are acceptable as self-signed for development/testing environments
- PostgreSQL and Redis services can be managed via standard package managers
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible
- Current Chef Solo deployment model will be replaced with Ansible playbook execution
- UFW firewall is the preferred firewall solution (vs iptables)
- The three configured domains (test.cluster.local, ci.cluster.local, status.cluster.local) represent the complete site requirements
- Static HTML files in cookbooks/nginx-multisite/files/default/ directories are the intended content for each subdomain
- Redis configuration patching via ruby_block indicates potential compatibility issues with the redisio cookbook that may not exist with direct Redis installation