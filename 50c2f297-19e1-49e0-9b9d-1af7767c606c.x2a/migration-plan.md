# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure setup for a multi-site nginx web server with caching services and a FastAPI application. The migration involves 3 custom cookbooks with moderate complexity, requiring approximately 3-4 weeks for complete migration including testing and validation.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
All module paths have been verified using directory listing and file search tools.

- **nginx-multisite**:
    - Description: Nginx reverse proxy with SSL-enabled multi-site configuration, security hardening via fail2ban/UFW, and self-signed certificate generation for development
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multiple SSL virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local), fail2ban intrusion prevention, UFW firewall configuration, SSH hardening, sysctl security tuning, custom lineinfile resource

- **cache**:
    - Description: Caching layer with memcached and Redis services, including Redis authentication and custom configuration fixes
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Memcached service, Redis 6379 with password authentication, custom Redis configuration cleanup via ruby_block, log directory management

- **fastapi-tutorial**:
    - Description: FastAPI Python web application with PostgreSQL database, systemd service management, and virtual environment setup
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git repository cloning from GitHub, Python virtual environment creation, PostgreSQL database and user provisioning, systemd service configuration, environment variable management

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4) and local cookbook references
- `solo.json`: Chef Solo run list configuration and node attributes for nginx sites, SSL paths, and security settings
- `solo.rb`: Chef Solo configuration with cookbook paths and logging settings
- `Vagrantfile`: Development environment setup using Fedora 42 with libvirt provider, port forwarding (80→8080, 443→8443), and rsync folder synchronization
- `vagrant-provision.sh`: Automated provisioning script for Chef installation, Berkshelf dependency resolution, and cookbook execution

### Target Details

- **Operating System**: Ubuntu 18.04+ or CentOS 7+ (based on cookbook metadata supports declarations)
- **Virtual Machine Technology**: Libvirt/KVM (based on Vagrantfile libvirt provider configuration)
- **Cloud Platform**: Not specified (local development focused with Vagrant)

## Migration Approach

### Key Dependencies to Address
- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and ansible.builtin.service modules
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks
- **Chef Solo**: Replace with Ansible playbooks and inventory management
- **Berkshelf**: Replace with Ansible Galaxy and requirements.yml for external role dependencies

### Security Considerations
- **Hardcoded credentials in cache cookbook**: Redis password 'redis_secure_password_123' needs to be moved to Ansible Vault
- **PostgreSQL credentials in fastapi-tutorial**: Database password 'fastapi_password' requires Vault encryption
- **SSL certificate management**: Self-signed certificate generation needs secure key handling and proper file permissions (640 for private keys, ssl-cert group membership)
- **SSH hardening configurations**: Root login disable and password authentication disable need careful validation
- **UFW firewall rules**: Port access controls (SSH, HTTP, HTTPS) require systematic migration to ensure no security gaps
- **Fail2ban jail configurations**: Intrusion prevention rules need template migration with proper service restart handling

### Technical Challenges
- **Custom lineinfile resource**: The nginx-multisite cookbook includes a custom Chef resource for file line management that needs replacement with Ansible's lineinfile module
- **Ruby block configuration fixes**: The cache cookbook uses ruby_block to manipulate Redis configuration files, requiring conversion to Ansible file manipulation tasks
- **Complex template dependencies**: Multiple ERB templates (nginx.conf, site.conf, security.conf, fail2ban.jail.local, sysctl-security.conf) need conversion to Jinja2
- **Service notification chains**: Chef's notifies/subscribes patterns for service reloads need careful mapping to Ansible handlers
- **Git repository management**: FastAPI tutorial cloning and virtual environment setup requires idempotent Ansible task design
- **PostgreSQL database provisioning**: Database and user creation with proper privilege management needs postgresql_* module implementation
- **Systemd service file management**: Custom service file creation and daemon-reload handling requires systemd module usage

### Migration Order
1. **cache cookbook** (low risk, foundational service) - Simple service installation with clear external dependencies
2. **fastapi-tutorial cookbook** (moderate complexity) - Application deployment with database dependencies but isolated functionality  
3. **nginx-multisite cookbook** (high complexity, multiple dependencies) - Complex multi-site configuration with security hardening, SSL management, and custom resources

### Assumptions
- Target systems will maintain Ubuntu/CentOS compatibility as specified in cookbook metadata
- External cookbook dependencies (nginx, memcached, redisio) functionality will be replicated using equivalent Ansible modules
- Development environment will transition from Vagrant+Chef to Vagrant+Ansible or direct Ansible execution
- SSL certificate management will remain self-signed for development environments (production may require Let's Encrypt or CA-signed certificates)
- Database credentials and Redis passwords will be properly secured using Ansible Vault in production deployments
- Network configuration (private network 192.168.121.10, port forwarding) may need adjustment based on target infrastructure
- The custom lineinfile resource functionality can be fully replaced by Ansible's built-in lineinfile module
- Ruby block configuration manipulation can be converted to equivalent Ansible file/replace/lineinfile tasks
- Service restart/reload patterns will maintain the same dependency chains through Ansible handlers
- Git repository access (https://github.com/dibanez/fastapi_tutorial.git) will remain available and accessible from target systems
- PostgreSQL service management and database provisioning will follow similar patterns with appropriate Ansible postgresql modules
- Systemd service management will be compatible across target operating systems
- File and directory permissions, ownership, and group memberships will be preserved during migration
- Template variable substitution from ERB to Jinja2 will maintain equivalent functionality
- Chef Solo execution model will be replaced with standard Ansible playbook execution without significant workflow changes