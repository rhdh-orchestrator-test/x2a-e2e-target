# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with nginx reverse proxy, caching services (Redis/Memcached), and a FastAPI Python application with PostgreSQL backend. The migration involves 3 custom cookbooks with moderate complexity, requiring approximately 4-6 weeks for complete migration including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx reverse proxy with SSL-enabled multi-site configuration, security hardening via fail2ban/UFW firewall, and SSH security controls
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multiple SSL virtual hosts (test/ci/status subdomains), fail2ban intrusion prevention, UFW firewall rules, SSH hardening (root login disabled, password auth disabled), sysctl security tuning

**cache**:
- Description: Caching services configuration with Redis authentication and Memcached setup, including custom Redis configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication (requirepass), Memcached service, custom log directory creation, configuration file patching via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service management, environment variable configuration

### Infrastructure Files

- `Berksfile`: Chef dependency management - defines external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4) and local cookbook paths
- `solo.json`: Chef Solo node configuration - contains run_list and attribute overrides for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration file for cookbook and data bag paths
- `Vagrantfile`: Development environment provisioning with Vagrant
- `vagrant-provision.sh`: Shell script for Vagrant VM provisioning

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support defined in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (based on Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or cloud-agnostic deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks
- **ssl_certificate (~> 2.1)**: Currently commented out - SSL certificate management needs custom Ansible solution

### Security Considerations

- **Hardcoded credentials**: Redis password "redis_secure_password_123" and PostgreSQL password "fastapi_password" are hardcoded in recipes - migrate to Ansible Vault
- **SSH security configurations**: Root login disabled, password authentication disabled - migrate to ansible.posix.sshd_config module
- **Firewall rules**: UFW configuration for ports 22, 80, 443 - migrate to community.general.ufw module
- **SSL certificate management**: SSL paths configured but certificate provisioning not automated - requires Let's Encrypt or manual certificate deployment strategy
- **Fail2ban configuration**: Intrusion prevention via template - migrate to community.general.fail2ban module
- **Credential types per module**:
  - cache: Redis authentication password (plaintext in attributes)
  - fastapi-tutorial: PostgreSQL database credentials (plaintext in recipe)
  - nginx-multisite: SSL certificate paths (no credential management visible)

### Technical Challenges

- **Ruby block configuration patching**: The cache cookbook uses a ruby_block to modify Redis configuration files post-installation - requires custom Ansible lineinfile/replace tasks or template-based approach
- **Git repository management**: FastAPI cookbook clones from GitHub - ensure Ansible git module handles repository updates and authentication properly
- **Multi-site nginx configuration**: Complex template-driven virtual host generation - migrate to ansible.builtin.template with Jinja2 templates
- **Service dependency ordering**: PostgreSQL must be running before database creation, nginx reload after configuration changes - use Ansible handlers and task dependencies
- **Python virtual environment management**: Manual venv creation and pip installation - migrate to ansible.builtin.pip with virtualenv parameters

### Migration Order

1. **cache** (low risk, high value) - Simple service installation with well-defined external dependencies
2. **nginx-multisite** (moderate complexity) - Core infrastructure component with security configurations and template management
3. **fastapi-tutorial** (high complexity, dependencies) - Application deployment requiring database setup, git operations, and service management

### Assumptions

- SSL certificates are manually managed or obtained through external processes (certificate provisioning not automated in current Chef setup)
- The target environment has internet access for package installation and git repository cloning
- PostgreSQL and Redis services will run on the same host as the web application (no external database configuration visible)
- The "cluster.local" domain names are resolvable in the target environment or will be configured via /etc/hosts
- Current Chef Solo deployment model suggests single-node deployment - Ansible playbook should target single host unless scaling requirements change
- Development environment uses Vagrant, but production deployment method is not specified in the repository
- The ruby_block configuration fixes in the cache cookbook indicate compatibility issues with the redisio cookbook version - this technical debt should be resolved in the Ansible migration rather than replicated