# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with caching services, security hardening, and SSL-enabled nginx reverse proxy. The migration involves 3 cookbooks with moderate complexity, requiring approximately 4-6 weeks for complete migration including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis authentication, including custom Redis configuration fixes and log directory management
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached service, Redis with password authentication, custom configuration patching via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python venv setup, PostgreSQL database/user creation, systemd service management

**nginx-multisite**:
- Description: Nginx reverse proxy with SSL-enabled multi-domain hosting, security hardening via fail2ban/UFW, and SSH configuration management
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, fail2ban integration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4) and local cookbook paths
- `solo.json`: Chef Solo run configuration with run_list and node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file for cookbook and data bag paths
- `Vagrantfile`: Development environment provisioning configuration
- `vagrant-provision.sh`: Bootstrap script for Vagrant environment setup

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox (based on Vagrantfile presence for development)
- **Cloud Platform**: Not specified - appears to be VM-based deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks

### Security Considerations

- **Hardcoded credentials**: Redis password "redis_secure_password_123" and PostgreSQL password "fastapi_password" are embedded in recipes - migrate to Ansible Vault
- **SSL certificate management**: SSL certificate paths defined in attributes (/etc/ssl/certs, /etc/ssl/private) - implement secure certificate deployment with Ansible Vault
- **SSH hardening**: Root login disabled, password authentication disabled - migrate to ansible.posix.sshd_config module
- **Firewall configuration**: UFW rules for SSH, HTTP, HTTPS - migrate to community.general.ufw module
- **Fail2ban integration**: Custom jail.local template - migrate to community.general.fail2ban module
- **Sysctl security tuning**: Custom security.conf template - migrate to ansible.posix.sysctl module
- **Database credentials**: PostgreSQL user/password creation via shell commands - migrate to community.postgresql.* modules with Ansible Vault

### Technical Challenges

- **Ruby block configuration patching**: The cache cookbook uses ruby_block to modify Redis configuration files post-installation - requires custom Ansible tasks with lineinfile or template modules
- **Git repository management**: FastAPI tutorial clones from GitHub with sync action - migrate to ansible.builtin.git module with proper version control
- **Multi-site nginx configuration**: Template-driven site configuration with dynamic document root creation - requires Jinja2 templates and loop constructs
- **Service dependency management**: PostgreSQL must be running before FastAPI service starts - implement proper task ordering and handlers
- **File permissions and ownership**: Multiple file/directory resources with specific ownership (www-data, redis) - ensure proper user/group management in Ansible

### Migration Order

1. **cache** (low risk, standalone service) - Redis and memcached services with minimal external dependencies
2. **nginx-multisite** (moderate complexity) - Web server configuration with security hardening, depends on SSL certificate management
3. **fastapi-tutorial** (high complexity) - Application deployment with database dependencies, requires coordination with nginx for reverse proxy setup

### Assumptions

- SSL certificates are manually managed and placed in /etc/ssl/certs and /etc/ssl/private - certificate provisioning process not defined in Chef cookbooks
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and stable during migration
- Target systems have internet access for package installation and git repository cloning
- PostgreSQL service configuration beyond basic installation is handled externally - no advanced database tuning present
- The "main" branch of the FastAPI repository is the intended deployment target
- UFW firewall rules are sufficient for the security model - no advanced iptables rules required
- Fail2ban configuration template (fail2ban.jail.local.erb) contains standard jail configurations - template content not examined
- Sysctl security configurations in sysctl-security.conf.erb follow standard hardening practices
- Redis configuration patching via ruby_block addresses specific version compatibility issues that may not apply to newer Redis versions in Ansible deployment
- Development environment uses Vagrant with VirtualBox - production deployment method not specified
- Node attributes in solo.json override cookbook defaults - attribute precedence must be maintained in Ansible variable structure