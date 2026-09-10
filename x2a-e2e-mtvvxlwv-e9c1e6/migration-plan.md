# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with 3 cookbooks managing web services, caching infrastructure, and a Python application stack. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to multi-service dependencies and security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx web server with multi-site SSL configuration, security hardening (fail2ban, UFW firewall), and SSH security controls
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: SSL certificate generation, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security tuning, multiple virtual hosts with SSL

**cache**:
- Description: Caching services configuration with memcached and Redis, including Redis authentication and custom configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication, memcached service, Redis log directory management, configuration file patching via ruby_block

**fastapi-tutorial**:
- Description: FastAPI Python application deployment with PostgreSQL database, virtual environment setup, and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment, PostgreSQL database and user creation, systemd service configuration, environment file management

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbook dependencies (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo configuration with run list and node attributes for site configurations and security settings
- `solo.rb`: Chef Solo execution configuration
- `Vagrantfile`: Development environment provisioning (requires review for Ansible equivalent)
- `vagrant-provision.sh`: Shell provisioning script for Vagrant integration

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support specified in metadata.rb files)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be local/on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom Redis configuration tasks

### Security Considerations

- **Hardcoded Credentials**: Redis password ('redis_secure_password_123') and PostgreSQL credentials ('fastapi_password') are hardcoded in recipes - migrate to Ansible Vault
- **SSL Certificate Management**: Self-signed certificate generation for development environments - consider Let's Encrypt integration for production
- **SSH Security Configuration**: Root login disable and password authentication disable via direct file modification - use ansible.posix.sshd_config module
- **Firewall Rules**: UFW configuration via shell commands - migrate to community.general.ufw module
- **Fail2ban Configuration**: Template-based jail configuration - use community.general.fail2ban module
- **Credential Types per Module**:
  - nginx-multisite: SSL certificate paths, no embedded credentials
  - cache: Redis authentication password (hardcoded)
  - fastapi-tutorial: PostgreSQL database credentials (hardcoded), application environment variables

### Technical Challenges

- **Ruby Block Workarounds**: The cache cookbook uses ruby_block to patch Redis configuration files - requires custom Ansible tasks with lineinfile or replace modules
- **Multi-Site SSL Management**: Dynamic SSL certificate generation per site requires Ansible loops and conditional logic
- **Service Dependencies**: PostgreSQL must be running before FastAPI application deployment - use Ansible handlers and service dependencies
- **Git Repository Management**: FastAPI cookbook clones from GitHub - ensure git module handles authentication and updates properly
- **Template Migration**: Convert ERB templates to Jinja2 format for nginx.conf, security.conf, and other configuration files

### Migration Order

1. **cache** (low risk, standalone service with clear dependencies)
2. **fastapi-tutorial** (moderate complexity, database dependencies but isolated application)
3. **nginx-multisite** (high complexity, security configurations and multi-site SSL management)

### Assumptions

- Current Chef cookbooks are used in development/testing environments (presence of Vagrant configuration)
- SSL certificates are self-signed for development purposes - production deployment may require different certificate management
- External cookbook dependencies (nginx, memcached, redisio) are compatible with target Ansible module versions
- PostgreSQL and Redis services will be managed by Ansible rather than external configuration management
- UFW firewall rules and fail2ban configurations are suitable for target environment security requirements
- Git repository access for FastAPI tutorial does not require authentication (public repository assumed)
- Systemd is available on target systems for service management (Ubuntu 18.04+ and CentOS 7+ support confirmed)
- Network connectivity allows package installation from default repositories and GitHub access for git operations