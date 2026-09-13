# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages web services, caching layers, and a FastAPI application with comprehensive security hardening. The migration involves 3 custom cookbooks with external dependencies, requiring careful coordination of service dependencies and security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx reverse proxy with SSL-enabled multi-site hosting, security hardening via fail2ban/UFW, and system-level security configurations
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multiple SSL virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local), fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security tuning

**cache**:
- Description: Dual caching layer with memcached and Redis services, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached service, Redis with password authentication, custom Redis configuration patching via ruby_block, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application with PostgreSQL database backend, systemd service management, and virtual environment setup
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment, PostgreSQL database and user creation, systemd service configuration, environment variable management

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbook versions (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list and node attributes configuration with site definitions and security settings
- `solo.rb`: Chef Solo configuration file for local cookbook execution
- `Vagrantfile`: Development environment provisioning (requires review for Ansible equivalent)
- `vagrant-provision.sh`: Shell provisioning script for Vagrant integration

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in metadata.rb files)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom Redis configuration tasks
- **Chef Solo execution model**: Replace with Ansible playbook execution targeting localhost or remote hosts

### Security Considerations

- **Hardcoded credentials**: Redis password "redis_secure_password_123" and PostgreSQL password "fastapi_password" in recipe files - migrate to Ansible Vault
- **SSL certificate management**: SSL certificate paths defined in attributes (/etc/ssl/certs, /etc/ssl/private) - ensure proper certificate deployment in Ansible
- **SSH hardening configurations**: Root login disabled, password authentication disabled - replicate in Ansible with lineinfile or sshd_config module
- **Firewall rules**: UFW configuration for HTTP/HTTPS/SSH - migrate to community.general.ufw module
- **Fail2ban configuration**: Custom jail.local template - migrate to template module with equivalent Jinja2 template
- **System security tuning**: sysctl security parameters - migrate to ansible.posix.sysctl module

### Technical Challenges

- **Ruby block configuration patching**: The cache cookbook uses a ruby_block to modify Redis configuration files post-installation - requires conversion to Ansible lineinfile or replace modules with proper regex patterns
- **Service dependency coordination**: Nginx depends on SSL certificates, FastAPI depends on PostgreSQL, all services have interdependencies - requires careful Ansible task ordering and handlers
- **Multi-site virtual host management**: Dynamic site creation from attributes requires Ansible loops and template generation for each virtual host
- **Git repository management**: FastAPI cookbook clones and updates Git repositories - migrate to ansible.builtin.git module with proper change detection
- **Python virtual environment handling**: Complex pip installation within venv requires ansible.builtin.pip module with virtualenv parameters

### Migration Order

1. **cache** (low risk, standalone service, clear dependencies)
2. **fastapi-tutorial** (moderate complexity, database dependencies, systemd service)
3. **nginx-multisite** (high complexity, security configurations, depends on other services for upstream backends)

### Assumptions

- SSL certificates are manually managed or provided by external processes (no automated certificate generation visible in cookbooks)
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and compatible with the current deployment method
- PostgreSQL installation uses default package manager versions rather than specific version requirements
- The current Chef Solo execution model suggests single-node deployment, but Ansible migration may target multiple hosts
- UFW firewall rules are sufficient for the security requirements (no iptables or other firewall solutions needed)
- The Redis configuration patching via ruby_block is a workaround for cookbook limitations rather than a business requirement
- Vagrant development environment will be replaced with equivalent Ansible testing methodology (molecule, vagrant with Ansible provisioner, or direct VM testing)
- Current hardcoded passwords are acceptable for development/testing but will need proper secret management for production deployment