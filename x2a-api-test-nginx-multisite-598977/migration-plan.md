# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with 3 cookbooks managing web services, caching infrastructure, and a FastAPI application. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to external dependencies and security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx web server with multi-site SSL configuration, security hardening via fail2ban/UFW, and system-level security controls
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: SSL-enabled virtual hosts for test/ci/status subdomains, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security parameters

**cache**:
- Description: Caching services configuration providing both memcached and Redis with authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication (redis_secure_password_123), memcached service, Redis log directory management, configuration file patching via Ruby blocks

**fastapi-tutorial**:
- Description: FastAPI Python web application with PostgreSQL database backend, systemd service management, and virtual environment setup
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment, PostgreSQL database and user creation, systemd service configuration, environment file management

### Infrastructure Files

- `Berksfile`: Chef dependency management - defines external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo configuration with run list and node attributes for site configurations and security settings
- `solo.rb`: Chef Solo configuration file for cookbook paths and execution settings
- `Vagrantfile`: Development environment provisioning - will need Ansible equivalent for local testing
- `vagrant-provision.sh`: Shell provisioning script - may contain additional setup steps to preserve

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be VM-based deployment

## Migration Approach

### Key Dependencies to Address
- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis modules or custom Redis configuration tasks

### Security Considerations
- **Hardcoded credentials**: Redis password (redis_secure_password_123) and PostgreSQL password (fastapi_password) are hardcoded in recipes - migrate to Ansible Vault
- **SSH hardening**: Root login disabled, password authentication disabled - preserve in Ansible tasks
- **Firewall configuration**: UFW rules for SSH, HTTP, HTTPS - convert to ansible.posix.ufw module
- **Fail2ban configuration**: Custom jail.local template - migrate template to Ansible with community.general.fail2ban
- **SSL certificates**: Certificate paths configured but certificate provisioning not visible in reviewed files
- **Sysctl security parameters**: Custom security.conf template for kernel parameters - preserve in Ansible

### Technical Challenges
- **Ruby block configuration patching**: The cache cookbook uses Ruby blocks to modify Redis configuration files post-installation - will need equivalent Ansible lineinfile or replace tasks
- **Complex service dependencies**: FastAPI service depends on PostgreSQL being ready - ensure proper Ansible task ordering and handlers
- **Template migration**: Multiple ERB templates (nginx.conf, security.conf, site.conf, fail2ban.jail.local, sysctl-security.conf) need conversion to Jinja2
- **Git repository management**: FastAPI cookbook clones from GitHub - ensure Ansible git module handles updates properly
- **Virtual environment management**: Python venv creation and pip installations need careful Ansible task sequencing

### Migration Order
1. **cache** (moderate complexity, no external service dependencies)
2. **nginx-multisite** (moderate complexity, security configurations, multiple templates)
3. **fastapi-tutorial** (highest complexity, database dependencies, service management)

### Assumptions
- SSL certificates are managed externally or through a separate process not visible in the reviewed cookbooks
- The target environment has internet access for package installation and git repository cloning
- PostgreSQL installation and initial setup is sufficient via package manager (no custom compilation or advanced configuration required)
- The Ruby block configuration fixes in the Redis setup are still necessary and not resolved in newer Redis versions
- The systemd service configuration for FastAPI is appropriate for the target deployment environment
- UFW is the preferred firewall solution (vs. iptables or firewalld)
- The current Chef Solo deployment model will be replaced with Ansible playbook execution (vs. Ansible Tower/AWX)