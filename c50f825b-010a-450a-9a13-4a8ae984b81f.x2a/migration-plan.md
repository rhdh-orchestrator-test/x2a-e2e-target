# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure setup with 3 cookbooks that provision a multi-site nginx web server with caching services and a FastAPI application. The migration involves converting Chef recipes, templates, and attributes to Ansible playbooks, roles, and Jinja2 templates. Estimated timeline: 2-3 weeks for a team of 2-3 engineers with moderate Chef and Ansible experience.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**nginx-multisite**:
- Description: Nginx reverse proxy with SSL termination, security hardening, multi-site configuration, fail2ban protection, UFW firewall, and system security tuning
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Self-signed SSL certificates, security headers, rate limiting, fail2ban integration, UFW firewall rules, SSH hardening, sysctl security tuning, custom lineinfile resource

**cache**:
- Description: Caching services configuration with memcached and Redis, including authentication and custom Redis configuration fixes
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with password authentication, memcached service, custom Redis configuration cleanup via ruby_block, log directory management

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment setup, and systemd service management
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python virtual environment, PostgreSQL database and user creation, systemd service configuration, environment file management

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef node attributes defining nginx sites configuration, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration with cookbook paths and logging settings
- `Vagrantfile`: Development environment setup with Fedora 42, network configuration, and Chef provisioning
- `vagrant-provision.sh`: Automated Chef installation and cookbook dependency resolution script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata.rb supports declarations)
- **Virtual Machine Technology**: Libvirt/KVM (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified (local development environment focused)

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks
- **Chef Solo runtime**: Replace with Ansible playbook execution and ansible-pull for solo mode
- **Berkshelf dependency management**: Replace with Ansible Galaxy requirements.yml and ansible-galaxy install

### Security Considerations

- **Hardcoded credentials in cache cookbook**: Redis password 'redis_secure_password_123' needs to be moved to Ansible Vault
- **PostgreSQL credentials in fastapi-tutorial**: Database password 'fastapi_password' requires Vault encryption
- **SSL certificate management**: Self-signed certificate generation needs secure key handling and proper file permissions
- **SSH security configurations**: Root login disable and password authentication disable need careful validation
- **Fail2ban and UFW configurations**: Security service management requires proper handler notifications
- **System security tuning**: sysctl parameters need validation and testing

Vault/secrets management: 
- **nginx-multisite**: 0 hardcoded credentials detected (SSL certificates are self-signed)
- **cache**: 1 hardcoded credential (Redis password in default recipe)
- **fastapi-tutorial**: 2 hardcoded credentials (PostgreSQL user password, database connection string in .env file)

### Technical Challenges

- **Custom lineinfile resource**: The nginx-multisite cookbook includes a custom Chef resource for line-in-file operations that needs conversion to ansible.builtin.lineinfile module with proper regex patterns
- **Ruby block configuration fixes**: The cache cookbook uses a ruby_block to manually edit Redis configuration files, requiring conversion to Ansible template or lineinfile operations
- **Complex template variables**: The site.conf.erb template uses conditional SSL configuration that needs careful conversion to Jinja2 with proper variable scoping
- **Service notification chains**: Multiple recipes use delayed notifications to reload nginx service, requiring proper Ansible handler implementation
- **File permission management**: SSL certificate and key files have specific ownership (root:ssl-cert) and permissions (640) that need precise replication
- **PostgreSQL database initialization**: The fastapi-tutorial uses shell commands with sudo -u postgres that need conversion to postgresql_* Ansible modules

### Migration Order

1. **cache cookbook** (low risk, simple services): Start with memcached and Redis configuration to establish patterns for service management and configuration files
2. **fastapi-tutorial cookbook** (moderate complexity): Python application deployment with database setup provides good learning for systemd service management
3. **nginx-multisite cookbook** (high complexity, dependencies): Complex multi-site configuration with security hardening, SSL, and custom resources should be migrated last

### Assumptions

- The target environment will maintain the same OS support (Ubuntu 18.04+, CentOS 7+) as specified in cookbook metadata
- Self-signed SSL certificates are acceptable for the target environment (production may require Let's Encrypt or CA-signed certificates)
- The Vagrant development environment pattern will be maintained with Ansible provisioning instead of Chef
- PostgreSQL and Redis services will be installed locally rather than using external managed services
- The three-site configuration (test.cluster.local, ci.cluster.local, status.cluster.local) represents the actual target deployment pattern
- Network configuration (192.168.121.10, port forwarding 8080->80, 8443->443) will remain consistent for development
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) is accessible and stable for deployment
- System security hardening requirements (fail2ban, UFW, SSH configuration, sysctl tuning) are mandatory for the target environment
- The custom Redis configuration cleanup (removing replica-* and client-output-buffer-limit directives) is still required for the target Redis version
- File ownership patterns (www-data for web content, ssl-cert group for private keys) are compatible with the target OS distribution