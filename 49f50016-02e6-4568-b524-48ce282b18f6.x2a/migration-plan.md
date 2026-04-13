# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks. The estimated timeline for this migration is 3-4 weeks, with moderate complexity due to the security configurations and multi-site SSL setup.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled subdomains, security hardening, and site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening with fail2ban and UFW

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, PostgreSQL database creation, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management file for Chef cookbooks, lists external dependencies from Chef Supermarket
- `Policyfile.rb`: Chef policy file defining the run list and cookbook dependencies
- `Vagrantfile`: Defines a Vagrant VM for testing with Fedora 42, will need conversion to Ansible-compatible testing
- `vagrant-provision.sh`: Shell script for provisioning the Vagrant VM with Chef
- `solo.json`: Chef node attributes configuration file, contains site configurations and security settings
- `solo.rb`: Chef solo configuration file

### Target Details

Based on the source configuration files:

- **Operating System**: Supports Ubuntu 18.04+ and CentOS 7.0+ (based on cookbook metadata), with Fedora 42 used for testing (from Vagrantfile)
- **Virtual Machine Technology**: Vagrant with libvirt provider (based on Vagrantfile)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role or community.general.nginx_* modules
- **memcached (~> 6.0)**: Replace with Ansible memcached role or package installation tasks
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role or direct configuration tasks
- **ssl_certificate (~> 2.1)**: Replace with Ansible OpenSSL modules for certificate generation

### Security Considerations

- **Firewall Configuration**: The Chef cookbook configures UFW; migrate to Ansible's `ufw` module
- **Fail2ban Setup**: Migrate fail2ban configuration to Ansible tasks using templates
- **SSH Hardening**: Migrate SSH security configurations (disable root login, password authentication) to Ansible tasks
- **SSL Certificate Management**: Migrate self-signed certificate generation to Ansible's `openssl_*` modules
- **Redis Authentication**: Ensure Redis password is stored securely in Ansible Vault
- **PostgreSQL Credentials**: Store database credentials in Ansible Vault

### Technical Challenges

- **Multi-site Configuration**: The nginx-multisite cookbook dynamically creates site configurations based on attributes; this pattern needs to be replicated in Ansible using loops and templates
- **SSL Certificate Generation**: Self-signed certificate generation needs to be migrated to Ansible's OpenSSL modules
- **Security Hardening**: Comprehensive security configurations need careful migration to maintain the same level of protection
- **Service Dependencies**: Ensure proper ordering of service installations and configurations in Ansible

### Migration Order

1. **cache role** (low complexity): Migrate Memcached and Redis configurations
2. **nginx-multisite role** (medium complexity): Migrate Nginx configuration, site setup, and SSL certificate generation
3. **fastapi-tutorial role** (medium complexity): Migrate Python application deployment, PostgreSQL setup, and service configuration

### Assumptions

1. The target environment will continue to be Ubuntu/CentOS based systems
2. Self-signed certificates are acceptable for the migrated solution (production would likely use Let's Encrypt)
3. The same security hardening measures are required in the Ansible version
4. The FastAPI application source will continue to be pulled from the same Git repository
5. Redis and PostgreSQL passwords in the Chef recipes are placeholders and will be replaced with secure passwords in Ansible Vault
6. The Vagrant testing environment should be preserved with similar functionality

## Implementation Details

### Ansible Structure

```
ansible/
├── inventories/
│   ├── development/
│   │   ├── group_vars/
│   │   │   └── all.yml  # Development environment variables
│   │   └── hosts        # Development inventory
│   └── production/
│       ├── group_vars/
│       │   └── all.yml  # Production environment variables
│       └── hosts        # Production inventory
├── roles/
│   ├── nginx-multisite/
│   │   ├── defaults/
│   │   │   └── main.yml  # Default variables (from Chef attributes)
│   │   ├── files/
│   │   │   └── (static files from Chef cookbook)
│   │   ├── handlers/
│   │   │   └── main.yml  # Handlers for service restarts
│   │   ├── tasks/
│   │   │   ├── main.yml
│   │   │   ├── nginx.yml
│   │   │   ├── security.yml
│   │   │   ├── sites.yml
│   │   │   └── ssl.yml
│   │   ├── templates/
│   │   │   ├── nginx.conf.j2
│   │   │   ├── security.conf.j2
│   │   │   ├── site.conf.j2
│   │   │   ├── fail2ban.jail.local.j2
│   │   │   └── sysctl-security.conf.j2
│   │   └── vars/
│   │       └── main.yml
│   ├── cache/
│   │   ├── defaults/
│   │   │   └── main.yml
│   │   ├── tasks/
│   │   │   ├── main.yml
│   │   │   ├── memcached.yml
│   │   │   └── redis.yml
│   │   ├── templates/
│   │   │   └── redis.conf.j2
│   │   └── vars/
│   │       └── main.yml
│   └── fastapi-tutorial/
│       ├── defaults/
│       │   └── main.yml
│       ├── tasks/
│       │   ├── main.yml
│       │   ├── app.yml
│       │   └── database.yml
│       ├── templates/
│       │   ├── env.j2
│       │   └── fastapi-tutorial.service.j2
│       └── vars/
│           └── main.yml
├── playbooks/
│   ├── site.yml          # Main playbook
│   ├── nginx.yml         # Nginx-specific playbook
│   ├── cache.yml         # Cache services playbook
│   └── fastapi.yml       # FastAPI application playbook
├── group_vars/
│   └── all/
│       ├── vars.yml      # Common variables
│       └── vault.yml     # Encrypted sensitive variables
└── ansible.cfg          # Ansible configuration
```

### Secrets Management

All sensitive information (Redis password, PostgreSQL credentials) should be stored in Ansible Vault:

```yaml
# group_vars/all/vault.yml (encrypted)
vault_redis_password: "secure_redis_password"
vault_postgres_user: "fastapi"
vault_postgres_password: "secure_postgres_password"
vault_postgres_db: "fastapi_db"
```

### Testing Strategy

1. Create a Vagrant-based testing environment similar to the existing one but using Ansible provisioning
2. Develop and test each role individually
3. Integrate roles and test the complete solution
4. Verify functionality matches the original Chef implementation

## Timeline Estimate

- **Week 1**: Analysis and planning, setup Ansible structure, create basic role skeletons
- **Week 2**: Implement cache and nginx-multisite roles
- **Week 3**: Implement fastapi-tutorial role, integrate all roles
- **Week 4**: Testing, documentation, and knowledge transfer

## Team Coordination

- Assign one developer per role for initial implementation
- Conduct regular sync meetings to address cross-role dependencies
- Establish code review process for each completed role
- Document all decisions and configurations in role READMEs