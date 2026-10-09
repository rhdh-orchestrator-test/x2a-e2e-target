# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing web services, caching infrastructure, and a Python application. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to external dependencies and security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx web server with multi-site SSL configuration, security hardening via fail2ban/UFW, and SSH security controls
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multiple SSL-enabled virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local), fail2ban intrusion prevention, UFW firewall configuration, SSH hardening (root login disabled, password auth disabled), sysctl security tuning

**cache**:
- Description: Caching infrastructure with memcached and Redis services, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Memcached service, Redis 6379 with authentication (requirepass), custom Redis configuration cleanup via ruby_block, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Python 3 virtual environment, Git repository cloning from GitHub, PostgreSQL database and user creation, systemd service management, environment configuration file

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Node configuration with run_list and attribute overrides for nginx sites and security settings
- `solo.rb`: Chef Solo configuration file for local cookbook execution
- `Vagrantfile`: Development environment provisioning (requires review for Ansible equivalent)
- `vagrant-provision.sh`: Shell provisioning script for Vagrant integration

### Target Details

- **Operating System**: Ubuntu 18.04+ or CentOS 7+ (based on metadata.rb supports declarations)
- **Virtual Machine Technology**: Vagrant/VirtualBox (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks

### Security Considerations

- **Hardcoded credentials**: Redis password 'redis_secure_password_123' and PostgreSQL password 'fastapi_password' are hardcoded in recipes - migrate to Ansible Vault
- **SSL certificate management**: SSL certificate paths configured but certificate deployment method unclear - implement proper certificate management with ansible.builtin.copy or community.crypto modules
- **SSH security**: Root login disabled and password authentication disabled - maintain these security controls in Ansible
- **Firewall configuration**: UFW rules for SSH (22), HTTP (80), HTTPS (443) - migrate to community.general.ufw module
- **Fail2ban configuration**: Intrusion prevention with custom jail.local template - migrate template to Ansible with ansible.builtin.template

### Technical Challenges

- **Ruby block configuration fixes**: The cache cookbook uses a ruby_block to modify Redis configuration files post-installation - replace with ansible.builtin.lineinfile or ansible.builtin.replace modules
- **Complex service dependencies**: FastAPI service depends on PostgreSQL being ready - implement proper service ordering with ansible.builtin.wait_for or handlers
- **Git repository management**: FastAPI cookbook clones from GitHub - migrate to ansible.builtin.git module with proper authentication handling
- **Template migration**: Multiple ERB templates (nginx.conf.erb, security.conf.erb, site.conf.erb, fail2ban.jail.local.erb, sysctl-security.conf.erb) need conversion to Jinja2
- **Attribute override complexity**: solo.json overrides cookbook attributes - migrate to Ansible group_vars/host_vars structure

### Migration Order

1. **cache** (low risk, foundational service) - Redis and memcached are standalone services with minimal dependencies
2. **nginx-multisite** (moderate complexity) - Web server with security configurations, depends on SSL certificate management
3. **fastapi-tutorial** (high complexity) - Application deployment with database dependencies, systemd service management, and Git integration

### Assumptions

- SSL certificates are manually managed or provided externally (no automated certificate generation found in cookbooks)
- The target environment has internet access for package installation and Git repository cloning
- PostgreSQL service configuration beyond basic setup is handled elsewhere (only basic database/user creation found)
- The Redis configuration "HACK" ruby_block suggests the redisio cookbook has compatibility issues that may not exist with direct Ansible Redis management
- Vagrant is used only for development/testing and production deployment uses a different mechanism
- The three nginx sites (test.cluster.local, ci.cluster.local, status.cluster.local) serve static content only based on the simple index.html files
- SSH key-based authentication is already configured on target systems (since password auth is disabled)
- The fail2ban configuration targets nginx-specific attack patterns (jail.local template not examined in detail)