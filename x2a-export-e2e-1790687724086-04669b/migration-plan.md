# MIGRATION FROM CHEF TO ANSIBLE

This repository contains a Chef-based infrastructure configuration that manages a multi-service web application stack with caching, security hardening, and SSL-enabled nginx reverse proxy. The migration involves 3 cookbooks with moderate complexity, estimated timeline of 2-3 weeks for a team of 2-3 engineers.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

**cache**:
- Description: Caching services configuration with memcached and Redis authentication, includes custom Redis configuration fixes and log directory management
- Path: cookbooks/cache
- Technology: Chef
- Key Features: Redis with authentication (password: redis_secure_password_123), memcached integration, custom config file manipulation, log directory creation

**fastapi-tutorial**:
- Description: FastAPI Python web application deployment with PostgreSQL database, virtual environment management, and systemd service configuration
- Path: cookbooks/fastapi-tutorial
- Technology: Chef
- Key Features: Git repository cloning, Python venv setup, PostgreSQL database/user creation, systemd service management, environment file configuration

**nginx-multisite**:
- Description: Nginx reverse proxy with multiple SSL-enabled subdomains, security hardening via fail2ban/UFW, and SSH configuration
- Path: cookbooks/nginx-multisite
- Technology: Chef
- Key Features: Multi-site SSL configuration, fail2ban jail configuration, UFW firewall rules, SSH hardening, sysctl security tuning

### Infrastructure Files

- `Berksfile`: Chef dependency management with external cookbooks (nginx ~> 12.0, memcached ~> 6.0, redisio ~> 7.2.4)
- `solo.json`: Chef Solo configuration with run list and node attributes for site configuration
- `solo.rb`: Chef Solo execution configuration
- `Vagrantfile`: Development environment provisioning
- `vagrant-provision.sh`: Vagrant provisioning script

### Target Details

- **Operating System**: Ubuntu 18.04+ and CentOS 7+ (multi-platform support specified in metadata.rb files)
- **Virtual Machine Technology**: Vagrant/VirtualBox (development), production platform not specified
- **Cloud Platform**: Not specified - appears to be on-premises or cloud-agnostic deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with ansible.builtin.package and community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with ansible.builtin.package and service management
- **redisio (~> 7.2.4)**: Replace with community.general.redis module or custom Redis configuration tasks

### Security Considerations

- **Hardcoded credentials**: Redis password (redis_secure_password_123) and PostgreSQL password (fastapi_password) are hardcoded in recipes - migrate to Ansible Vault
- **SSL certificate management**: SSL certificates referenced in nginx configuration need secure deployment mechanism
- **SSH hardening**: Root login disabled, password authentication disabled - preserve in Ansible
- **Firewall configuration**: UFW rules for HTTP/HTTPS/SSH need migration to ansible.posix.firewalld or ufw modules
- **Fail2ban configuration**: Custom jail.local template needs migration to Ansible template
- **Sysctl security tuning**: Security kernel parameters configured via template

### Technical Challenges

- **Custom Redis configuration manipulation**: Chef ruby_block performs regex-based config file editing - needs conversion to Ansible lineinfile or template approach
- **Multi-site nginx configuration**: Dynamic site creation based on node attributes requires Ansible loops and templating
- **PostgreSQL database initialization**: SQL commands executed via shell need migration to postgresql_* modules
- **Systemd service management**: Custom service file creation and daemon-reload handling
- **Git repository management**: FastAPI app deployment from Git requires ansible.builtin.git module
- **Python virtual environment**: Complex pip and venv management needs ansible.builtin.pip module

### Migration Order

1. **cache** (moderate complexity, standalone caching services)
2. **nginx-multisite** (high complexity due to multi-site configuration and security hardening)
3. **fastapi-tutorial** (moderate complexity, depends on database and application deployment)

### Assumptions

- SSL certificates are manually managed or obtained via external process (no automated certificate generation visible)
- PostgreSQL service is expected to be running on the same host as the application
- Redis and memcached services run on default ports without clustering
- UFW is the preferred firewall solution (no iptables or firewalld configuration present)
- The FastAPI application repository (https://github.com/dibanez/fastapi_tutorial.git) remains accessible and stable
- Development environment uses Vagrant, but production deployment method is not specified
- Node attributes in solo.json represent the desired production configuration
- All services run as root or www-data user (no complex user management requirements)
- Network configuration assumes single-host deployment (no load balancing or clustering visible)