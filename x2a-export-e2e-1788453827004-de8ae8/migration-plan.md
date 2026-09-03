# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef Solo configuration for a multi-site nginx web server with caching services and a FastAPI application. The migration involves 3 cookbooks with moderate complexity, including security hardening, SSL certificate management, and database configuration. Estimated timeline: 2-3 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
All module paths have been verified using directory listing and file search tools.

- **nginx-multisite**:
    - Description: Nginx reverse proxy with SSL-enabled multi-site configuration, security hardening via fail2ban/UFW, and self-signed certificate generation for development environments
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multiple SSL virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local), fail2ban intrusion detection, UFW firewall configuration, SSH hardening, sysctl security tuning, custom lineinfile resource

- **cache**:
    - Description: Caching layer with memcached and Redis services, including Redis authentication and custom configuration fixes
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Memcached service, Redis with password authentication (redis_secure_password_123), custom Redis configuration cleanup via ruby_block, log directory management

- **fastapi-tutorial**:
    - Description: FastAPI Python web application with PostgreSQL database backend, systemd service management, and virtual environment setup
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository cloning from GitHub, Python virtual environment creation, PostgreSQL database and user provisioning, systemd service configuration, environment variable management

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4) and local cookbook references
- `solo.json`: Chef Solo run list and node attributes including nginx site configurations, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration with cookbook paths and logging settings
- `Vagrantfile`: Development environment setup using Fedora 42 with libvirt provider, port forwarding (80→8080, 443→8443), and rsync folder synchronization
- `vagrant-provision.sh`: Automated Chef installation and Berkshelf dependency resolution script

### Target Details

- **Operating System**: Ubuntu 18.04+ or CentOS 7+ (based on cookbook metadata.rb supports declarations). Default to Red Hat Enterprise Linux 9 for standardization.
- **Virtual Machine Technology**: Libvirt/KVM (based on Vagrantfile libvirt provider configuration)
- **Cloud Platform**: Not specified - appears to be on-premises or local development environment

## Migration Approach

### Key Dependencies to Address
- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks
- **berkshelf**: Replace with ansible-galaxy for role dependency management
- **chef-solo**: Replace with ansible-playbook execution

### Security Considerations
- **Hardcoded Redis password**: The cache cookbook contains hardcoded Redis password 'redis_secure_password_123' in recipes/default.rb - migrate to Ansible Vault
- **PostgreSQL credentials**: FastAPI cookbook has hardcoded database password 'fastapi_password' - migrate to Ansible Vault
- **SSL certificate management**: Self-signed certificates generated via OpenSSL commands - consider Let's Encrypt integration or proper certificate management
- **SSH hardening**: Root login disabled, password authentication disabled - preserve these security settings in Ansible
- **Firewall configuration**: UFW rules for SSH, HTTP, HTTPS - maintain equivalent iptables or firewalld rules
- **Fail2ban configuration**: Intrusion detection for nginx - preserve jail configurations
- **Sysctl security tuning**: Kernel parameter hardening - maintain security.conf settings

### Technical Challenges
- **Custom Ruby resource (lineinfile)**: The nginx-multisite cookbook includes a custom Chef resource for line-in-file operations - replace with ansible.builtin.lineinfile module
- **Ruby block configuration fixes**: Cache cookbook uses ruby_block to manipulate Redis config files - convert to Ansible template or lineinfile operations
- **Complex nginx site templating**: Multiple ERB templates for nginx configuration - convert to Jinja2 templates with equivalent logic
- **Git repository cloning**: FastAPI cookbook clones from GitHub - use ansible.builtin.git module with proper authentication
- **Systemd service management**: Custom systemd unit file creation - use ansible.builtin.systemd and ansible.builtin.template modules
- **PostgreSQL database provisioning**: SQL commands executed via shell - use community.postgresql.* modules for idempotent database management

### Migration Order
1. **cache** (low risk, minimal dependencies) - Start with caching services as they have fewer external dependencies
2. **fastapi-tutorial** (moderate complexity) - Application deployment with database dependencies
3. **nginx-multisite** (high complexity, security dependencies) - Complex nginx configuration with security hardening as final integration layer

### Assumptions
- The target environment will maintain the same network configuration (192.168.121.10 private network)
- Self-signed certificates are acceptable for development environments (production would require proper CA-signed certificates)
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and stable
- PostgreSQL and Redis services will be managed by the same host (no external database servers)
- The Fedora 42 base OS in Vagrant can be replaced with RHEL 9 or equivalent for production
- SSH key-based authentication is already configured for the target systems
- The current Chef Solo approach (single-node, no Chef Server) translates to Ansible playbook execution without AWX/Tower
- External cookbook dependencies (nginx, memcached, redisio) functionality can be replicated with native Ansible modules
- The development workflow using Vagrant will be preserved with ansible-playbook provisioning
- SSL certificate paths (/etc/ssl/certs, /etc/ssl/private) and permissions (ssl-cert group) will be maintained
- The custom lineinfile resource functionality is adequately covered by Ansible's built-in lineinfile module
- Redis configuration cleanup (removing replica-* directives) is still necessary and will be handled via Ansible tasks
- The three-site configuration (test.cluster.local, ci.cluster.local, status.cluster.local) represents the complete scope