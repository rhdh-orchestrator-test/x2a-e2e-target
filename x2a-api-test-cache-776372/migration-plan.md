# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration with three cookbooks managing web services, caching, and application deployment. The migration involves converting Chef cookbooks to Ansible playbooks and roles, with moderate complexity due to multi-service dependencies and security configurations. Estimated timeline: 4-6 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx reverse proxy with SSL-enabled multi-site hosting, security hardening via fail2ban/UFW, and system-level security configurations
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multiple SSL virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local), fail2ban intrusion prevention, UFW firewall rules, SSH hardening, sysctl security tuning

**cache**:
- Description: Caching services configuration with Memcached and Redis, including authentication and custom Redis configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication, custom log directory setup, configuration file patching via Ruby blocks, Memcached integration

**fastapi-tutorial**:
- Description: FastAPI Python application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment setup, PostgreSQL database and user creation, systemd service management, environment variable configuration

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo run list configuration and node attributes for all three cookbooks
- `solo.rb`: Chef Solo configuration file
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support specified in cookbook metadata)
- **Virtual Machine Technology**: Vagrant/VirtualBox for development (inferred from Vagrantfile presence)
- **Cloud Platform**: Not specified - appears to be on-premises or cloud-agnostic deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis_* modules or custom Redis configuration tasks

### Security Considerations

- **Hardcoded Credentials**: Redis password ('redis_secure_password_123') and PostgreSQL credentials ('fastapi_password') are embedded in recipes - migrate to Ansible Vault
- **SSL Certificate Management**: SSL certificate paths defined in attributes (/etc/ssl/certs, /etc/ssl/private) - implement secure certificate deployment with Ansible Vault
- **SSH Hardening**: Root login disabled, password authentication disabled - preserve these security configurations in Ansible
- **Firewall Configuration**: UFW rules for SSH, HTTP, HTTPS - migrate to ansible.posix.ufw module
- **Fail2ban Integration**: Intrusion prevention with custom jail configuration - migrate to community.general.fail2ban module
- **System Security**: Custom sysctl security parameters - migrate to ansible.posix.sysctl module
- **Credential Types per Module**:
  - nginx-multisite: SSL certificate references, no embedded secrets
  - cache: Redis authentication password (hardcoded)
  - fastapi-tutorial: PostgreSQL database credentials (hardcoded), application environment variables

### Technical Challenges

- **Ruby Block Logic**: The cache cookbook contains custom Ruby code for Redis configuration file manipulation - requires conversion to Ansible lineinfile or template modules
- **Multi-Site SSL Configuration**: Complex nginx virtual host templating with SSL - migrate to Jinja2 templates with proper certificate management
- **Service Dependencies**: PostgreSQL must be running before FastAPI application starts - implement proper task ordering and handlers
- **Git Repository Management**: FastAPI cookbook clones from GitHub - ensure proper Git module usage with idempotency
- **Python Virtual Environment**: Complex pip and venv management - use ansible.builtin.pip with virtualenv parameters

### Migration Order

1. **cache** (low risk, standalone service with clear dependencies)
2. **nginx-multisite** (moderate complexity, foundational web service)
3. **fastapi-tutorial** (high complexity, depends on PostgreSQL and has application-specific requirements)

### Assumptions

- SSL certificates are manually managed and placed in standard locations (/etc/ssl/certs, /etc/ssl/private)
- The FastAPI tutorial repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and stable
- Current Chef Solo deployment model will be replaced with Ansible playbook execution
- Target systems have internet access for package installation and Git repository cloning
- PostgreSQL service configuration beyond basic setup is handled externally
- The three virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local) represent actual DNS entries in the target environment
- Vagrant development environment will be replaced with equivalent Ansible-based local testing
- External cookbook dependencies (nginx, memcached, redisio) functionality will be replicated using native Ansible modules rather than community roles