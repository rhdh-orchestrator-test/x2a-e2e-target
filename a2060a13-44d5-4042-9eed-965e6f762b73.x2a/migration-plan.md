# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks, handling external dependencies, and ensuring proper security configurations are maintained.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible Roles: 3-4 weeks
- Testing and Validation: 2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 7-8 weeks

**Complexity Assessment:** Medium
- Multiple interconnected services
- Security configurations that need careful migration
- Database and application deployment requirements

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Configures Nginx with multiple SSL-enabled virtual hosts, security hardening, and site-specific configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, UFW firewall)

- **cache**:
    - Description: Configures caching services including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Deploys a FastAPI Python application with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Defines cookbook dependencies (nginx, ssl_certificate, memcached, redisio) - will be replaced by Ansible Galaxy requirements
- `Policyfile.rb`: Defines the run list and cookbook versions - will be replaced by Ansible playbook structure
- `solo.json`: Contains node configuration data - will be migrated to Ansible inventory variables
- `Vagrantfile`: Defines the development VM - will need updating to use Ansible provisioner
- `vagrant-provision.sh`: Installs Chef and runs the cookbooks - will be replaced with Ansible provisioning

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or local development environments

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role (e.g., geerlingguy.nginx)
- **ssl_certificate (~> 2.1)**: Replace with Ansible modules for certificate management (openssl_* modules)
- **memcached (~> 6.0)**: Replace with Ansible memcached role (e.g., geerlingguy.memcached)
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role (e.g., geerlingguy.redis)

### Security Considerations

- **SSL Certificate Management**: Migrate self-signed certificate generation to Ansible's openssl_certificate module
- **Firewall Configuration (UFW)**: Use Ansible's ufw module to maintain firewall rules
- **Fail2ban Configuration**: Create Ansible tasks to install and configure fail2ban
- **SSH Hardening**: Maintain SSH security settings using Ansible's lineinfile or template modules
- **Redis Authentication**: Ensure Redis password is stored securely in Ansible Vault
- **PostgreSQL Credentials**: Store database credentials in Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: The current setup manages multiple virtual hosts with SSL. This will require careful templating in Ansible.
  - Mitigation: Create a flexible Jinja2 template system with variable-driven site configurations
  
- **Service Interdependencies**: The FastAPI application depends on PostgreSQL, and the web server depends on the application.
  - Mitigation: Use Ansible handlers and proper task ordering to ensure services start in the correct sequence

- **SSL Certificate Management**: Self-signed certificates are generated for each site.
  - Mitigation: Create a reusable Ansible role for certificate management

- **Security Hardening**: Multiple security layers are implemented.
  - Mitigation: Create a dedicated security role that can be applied consistently

### Migration Order

1. **Base Infrastructure Role** (low complexity)
   - System packages
   - Basic security configurations
   
2. **Cache Services Role** (medium complexity)
   - Memcached configuration
   - Redis with authentication
   
3. **FastAPI Application Role** (medium complexity)
   - PostgreSQL database setup
   - Python environment and application deployment
   - Systemd service configuration
   
4. **Nginx Multi-site Role** (high complexity)
   - SSL certificate generation
   - Virtual host configuration
   - Security hardening

### Assumptions

1. The target environment will continue to be Fedora-based systems (the current Vagrantfile specifies Fedora 42)
2. Self-signed certificates are acceptable for development (production would likely use Let's Encrypt or other CA)
3. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git will remain available
4. The current security configurations (fail2ban, UFW, SSH hardening) are appropriate for the target environment
5. Redis authentication password "redis_secure_password_123" will need to be stored securely in Ansible Vault
6. PostgreSQL credentials (fastapi/fastapi_password) will need to be stored securely in Ansible Vault
7. The current directory structure in /opt/ and /var/www/ should be maintained for compatibility

## Ansible Structure Recommendation

```
ansible-nginx-multisite/
├── inventories/
│   ├── development/
│   │   ├── group_vars/
│   │   │   └── all/
│   │   │       ├── vars.yml
│   │   │       └── vault.yml  # For secrets
│   │   └── hosts
│   └── production/
├── roles/
│   ├── nginx-multisite/
│   ├── cache-services/
│   ├── fastapi-app/
│   └── security/
├── playbooks/
│   ├── site.yml
│   ├── nginx.yml
│   ├── cache.yml
│   └── fastapi.yml
├── requirements.yml  # Ansible Galaxy requirements
└── Vagrantfile  # Updated for Ansible
```

## Testing Strategy

1. Develop and test each role individually using Molecule
2. Create integration tests to verify interactions between components
3. Use the existing Vagrant setup with Ansible provisioner to validate the complete stack
4. Implement idempotence tests to ensure configurations can be applied repeatedly