# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx configuration with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting three Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:** 3-4 weeks
**Complexity:** Medium
**Team Size Recommendation:** 2-3 engineers (1 lead, 1-2 implementers)

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
    - Key Features: Python virtual environment setup, Git repository deployment, PostgreSQL database configuration, systemd service management

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks - will be replaced by Ansible Galaxy requirements.yml
- `Policyfile.rb`: Chef policy definition - will be replaced by Ansible playbook structure
- `solo.rb`: Chef Solo configuration - will be replaced by Ansible configuration
- `solo.json`: Chef node attributes - will be migrated to Ansible group_vars and host_vars
- `Vagrantfile`: VM configuration for testing - can be adapted for Ansible testing
- `vagrant-provision.sh`: Provisioning script - will be replaced by Ansible provisioning

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile), with support for Ubuntu 18.04+ and CentOS 7+ (based on cookbook metadata)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic VM deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role from Galaxy or custom role
- **memcached (~> 6.0)**: Replace with Ansible memcached role from Galaxy or custom role
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role from Galaxy or custom role
- **ssl_certificate (~> 2.1)**: Replace with Ansible certificate management modules (openssl_*)

### Security Considerations

- **SSL Certificate Management**: Migration must preserve self-signed certificate generation for development environments
- **Firewall Configuration (UFW)**: Convert UFW rules to Ansible ufw module or firewalld for Fedora
- **fail2ban Configuration**: Migrate fail2ban configuration to Ansible fail2ban role
- **SSH Hardening**: Preserve SSH security settings (disable root login, password authentication)
- **Redis Authentication**: Ensure Redis password is properly managed in Ansible Vault
- **PostgreSQL Authentication**: Secure database credentials using Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of multiple site configurations needs careful translation to Ansible templates
- **SSL Certificate Management**: Self-signed certificate generation logic needs to be preserved
- **Security Hardening**: Comprehensive security measures need to be maintained across firewall, SSH, and system settings
- **Service Dependencies**: Ensure proper ordering of service deployments (database before application, etc.)

### Migration Order

1. **Base Infrastructure** (low complexity)
   - Convert Vagrant setup to use Ansible provisioner
   - Set up Ansible directory structure and inventory

2. **nginx-multisite Role** (medium complexity)
   - Create Nginx installation and configuration
   - Implement SSL certificate generation
   - Configure multi-site setup
   - Implement security hardening (fail2ban, UFW)

3. **cache Role** (medium complexity)
   - Implement Memcached configuration
   - Implement Redis with authentication

4. **fastapi-tutorial Role** (high complexity)
   - Set up PostgreSQL database
   - Configure Python environment
   - Deploy application from Git
   - Configure systemd service

### Assumptions

1. The current Chef setup is functional and represents the desired end state
2. Self-signed certificates are acceptable for the target environment (production would likely use different certificate management)
3. The security settings (firewall, SSH hardening) are appropriate for the target environment
4. The Redis password and PostgreSQL credentials in the Chef recipes are development values and will be replaced with Ansible Vault secured values
5. The FastAPI application repository at https://github.com/dibanez/fastapi_tutorial.git is accessible and contains the expected code
6. The Nginx sites configuration (test.cluster.local, ci.cluster.local, status.cluster.local) represents the actual desired hostnames

## Implementation Plan

### 1. Setup Phase (Week 1)

- Create Ansible directory structure following best practices
- Set up Ansible Galaxy requirements.yml for external dependencies
- Configure inventory structure for development, staging, and production
- Set up Ansible Vault for secrets management
- Create base playbook structure

### 2. Role Development Phase (Weeks 2-3)

- Develop nginx-multisite role
  - Implement Nginx installation and configuration
  - Create templates for site configurations
  - Implement SSL certificate generation
  - Configure security features

- Develop cache role
  - Implement Memcached configuration
  - Implement Redis with authentication

- Develop fastapi-tutorial role
  - Configure PostgreSQL database
  - Set up Python environment
  - Implement application deployment
  - Configure systemd service

### 3. Testing and Integration Phase (Week 4)

- Update Vagrantfile to use Ansible provisioner
- Create comprehensive test playbooks
- Verify functionality matches original Chef implementation
- Document the new Ansible implementation
- Create migration guide for operations team

## Recommended Ansible Structure

```
ansible/
├── ansible.cfg
├── inventory/
│   ├── group_vars/
│   │   ├── all.yml
│   │   └── webservers.yml
│   ├── host_vars/
│   │   └── webserver1.yml
│   └── hosts
├── playbooks/
│   ├── site.yml
│   ├── webservers.yml
│   └── database.yml
├── roles/
│   ├── nginx-multisite/
│   │   ├── defaults/
│   │   ├── handlers/
│   │   ├── tasks/
│   │   ├── templates/
│   │   └── files/
│   ├── cache/
│   │   ├── defaults/
│   │   ├── handlers/
│   │   ├── tasks/
│   │   └── templates/
│   └── fastapi-tutorial/
│       ├── defaults/
│       ├── handlers/
│       ├── tasks/
│       └── templates/
└── requirements.yml
```

## Knowledge Transfer Recommendations

1. Schedule a walkthrough of the Chef cookbooks with the development team
2. Document all configuration parameters and their Ansible equivalents
3. Create a mapping document between Chef resources and Ansible modules
4. Develop a testing strategy to verify equivalent functionality
5. Create runbooks for common operational tasks using the new Ansible playbooks