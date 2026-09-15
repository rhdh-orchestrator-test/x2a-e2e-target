# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that provisions a multi-service web application stack with nginx reverse proxy, caching services (Redis/Memcached), and a FastAPI application with PostgreSQL backend. The migration involves 3 cookbooks with moderate complexity, estimated timeline of 2-3 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx web server with SSL-enabled multi-site configuration, security hardening via fail2ban/UFW firewall, and SSH security controls
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multiple SSL virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local), fail2ban intrusion prevention, UFW firewall rules, SSH hardening (root login disabled, password auth disabled), sysctl security tuning

**cache**:
- Description: Caching services layer providing both Redis and Memcached with authentication and custom configuration management
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis 6379 with password authentication (redis_secure_password_123), Memcached service, custom Redis configuration cleanup via ruby_block, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application with PostgreSQL database backend, including full application lifecycle management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Python 3 virtual environment, Git repository cloning from GitHub, PostgreSQL database and user provisioning, systemd service management, environment configuration via .env file

### Infrastructure Files

- `Berksfile`: Chef dependency management defining external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run configuration with cookbook run_list and node attributes for site configuration
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning for local testing
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be infrastructure-agnostic

## Migration Approach

### Key Dependencies to Address
- **nginx (~> 12.0)**: Replace with ansible.builtin.package and ansible.builtin.template modules for nginx configuration
- **memcached (~> 6.0)**: Replace with community.general.memcached or ansible.builtin.package for memcached installation
- **redisio (~> 7.2.4)**: Replace with community.general.redis or ansible.builtin.package for Redis installation and configuration

### Security Considerations
- **Hardcoded credentials**: Redis password (redis_secure_password_123) and PostgreSQL credentials (fastapi:fastapi_password) are embedded in recipes - migrate to Ansible Vault
- **SSL certificate management**: SSL certificates referenced in nginx configuration need secure deployment mechanism via Ansible Vault or external certificate management
- **SSH security controls**: Root login disabled and password authentication disabled - preserve these security settings in Ansible playbooks
- **Firewall configuration**: UFW rules for SSH (22), HTTP (80), HTTPS (443) - maintain firewall security posture
- **Fail2ban configuration**: Intrusion prevention system configuration needs migration to Ansible fail2ban role
- **Sysctl security tuning**: Kernel security parameters configured via template - preserve security hardening

### Technical Challenges
- **Ruby block configuration cleanup**: The cache cookbook uses a ruby_block to modify Redis configuration files post-installation - this custom logic needs to be replicated using Ansible lineinfile or replace modules
- **Multi-site nginx configuration**: Complex nginx virtual host templating with SSL for multiple subdomains requires careful Ansible template migration
- **Service orchestration**: Proper service startup order (PostgreSQL before FastAPI, nginx after SSL configuration) needs to be maintained in Ansible playbook task ordering
- **Git repository management**: FastAPI application deployment via git clone needs migration to ansible.builtin.git module with proper change detection
- **Python virtual environment**: Virtual environment creation and pip dependency installation requires ansible.builtin.pip module configuration

### Migration Order
1. **cache** (low risk, foundational service) - Redis and Memcached services with minimal external dependencies
2. **fastapi-tutorial** (moderate complexity) - Application deployment with database dependencies but isolated functionality  
3. **nginx-multisite** (high complexity, dependencies) - Web server configuration depends on application services being available and requires SSL certificate management

### Assumptions
- SSL certificates for the three domains (test.cluster.local, ci.cluster.local, status.cluster.local) are available and will be managed outside of this migration or via Ansible Vault
- The FastAPI tutorial GitHub repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and the main branch is stable
- Target systems have internet connectivity for package installation and git repository access
- PostgreSQL installation and configuration requirements are compatible with target OS versions
- The current Chef Solo execution model will be replaced with Ansible playbook execution via ansible-playbook command
- UFW firewall rules and fail2ban configuration are appropriate for the target deployment environment
- The systemd service management approach is compatible with target systems (systemd-based distributions)
- Python 3 and pip are available on target systems or can be installed via package manager