# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a Chef-based infrastructure setup for a multi-site Nginx web server with caching services (Redis and Memcached) and a FastAPI application backed by PostgreSQL. The migration to Ansible will involve converting 3 Chef cookbooks with their dependencies to equivalent Ansible roles and playbooks.

**Estimated Timeline:**
- Analysis and Planning: 1 week
- Development of Ansible roles: 2-3 weeks
- Testing and Validation: 1-2 weeks
- Documentation and Knowledge Transfer: 1 week
- Total: 5-7 weeks

**Complexity Assessment:** Medium
- The codebase is well-structured with clear separation of concerns
- External dependencies on community cookbooks will need Ansible equivalents
- Security configurations need careful migration to maintain hardening standards

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **nginx-multisite**:
    - Description: Nginx web server with multiple SSL-enabled virtual hosts, security hardening, and custom site configurations
    - Path: cookbooks/nginx-multisite
    - Technology: Chef
    - Key Features: Multi-site configuration, SSL certificate generation, security hardening (fail2ban, ufw)

- **cache**:
    - Description: Caching services configuration including Memcached and Redis with authentication
    - Path: cookbooks/cache
    - Technology: Chef
    - Key Features: Redis with password authentication, Memcached configuration

- **fastapi-tutorial**:
    - Description: Python FastAPI application deployment with PostgreSQL database backend
    - Path: cookbooks/fastapi-tutorial
    - Technology: Chef
    - Key Features: Git-based deployment, Python virtual environment, PostgreSQL database setup, systemd service configuration

### Infrastructure Files

- `Berksfile`: Dependency management for Chef cookbooks - will be replaced by Ansible Galaxy requirements.yml
- `Policyfile.rb`: Chef policy definition - will be replaced by Ansible playbook structure
- `solo.json`: Chef node configuration - will be replaced by Ansible inventory and group_vars
- `solo.rb`: Chef configuration - will be replaced by ansible.cfg
- `Vagrantfile`: Development environment definition - can be adapted for Ansible testing
- `vagrant-provision.sh`: Provisioning script - will be replaced by Ansible playbook calls

### Target Details

- **Operating System**: Fedora 42 (based on Vagrantfile configuration)
- **Virtual Machine Technology**: Libvirt (based on Vagrantfile provider configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **nginx (~> 12.0)**: Replace with Ansible nginx role from Galaxy or custom role
- **memcached (~> 6.0)**: Replace with Ansible memcached role from Galaxy or custom role
- **redisio (~> 7.2.4)**: Replace with Ansible Redis role from Galaxy or custom role
- **ssl_certificate (~> 2.1)**: Replace with Ansible certificate management tasks or community.crypto collection

### Security Considerations

- **Firewall (UFW)**: Migrate UFW rules to Ansible firewalld or ufw module
- **Fail2ban**: Migrate fail2ban configuration to Ansible fail2ban role
- **SSH Hardening**: Migrate SSH security settings using Ansible's openssh_config module
- **SSL Certificates**: Ensure secure handling of certificates using Ansible's crypto modules
- **Redis Password**: Store Redis password in Ansible Vault instead of plaintext
- **PostgreSQL Credentials**: Store database credentials in Ansible Vault

### Technical Challenges

- **Multi-site Nginx Configuration**: The dynamic generation of multiple virtual hosts with SSL will require careful templating in Ansible
- **SSL Certificate Generation**: Self-signed certificate generation logic needs to be replicated in Ansible
- **Redis Configuration Hacks**: The current Chef recipe includes a hack to fix Redis configuration which will need a clean implementation in Ansible
- **Service Orchestration**: Ensuring proper service restart handlers and dependencies are maintained in Ansible

### Migration Order

1. **nginx-multisite** (moderate complexity, foundation for other services)
   - Create base Nginx role
   - Implement security hardening (fail2ban, ufw)
   - Implement SSL certificate generation
   - Configure virtual hosts

2. **cache** (low complexity, independent service)
   - Implement Memcached configuration
   - Implement Redis with authentication

3. **fastapi-tutorial** (high complexity, depends on PostgreSQL)
   - Implement PostgreSQL database setup
   - Implement Python application deployment
   - Configure systemd service

### Assumptions

1. The target environment will continue to be Fedora-based systems
2. Self-signed certificates are acceptable for development (production would likely use Let's Encrypt or other CA)
3. The same security hardening requirements will apply in the new environment
4. The FastAPI application repository will remain available at the specified URL
5. The current directory structure in the target environment (/opt/server/*, /etc/ssl/*) should be maintained
6. Redis and Memcached configurations don't have specific tuning requirements beyond what's in the current recipes

## Ansible Structure Recommendation

```
ansible-nginx-multisite/
├── ansible.cfg
├── inventory/
│   ├── hosts
│   └── group_vars/
│       ├── all.yml
│       └── webservers.yml
├── playbooks/
│   ├── site.yml
│   ├── nginx.yml
│   ├── cache.yml
│   └── fastapi.yml
├── roles/
│   ├── nginx-multisite/
│   ├── cache/
│   └── fastapi-tutorial/
├── requirements.yml
└── Vagrantfile
```

## Testing Strategy

1. Create a Vagrant environment similar to the current one but using Ansible provisioner
2. Implement automated testing using Molecule
3. Create verification tests to ensure:
   - Nginx sites are properly configured and accessible
   - SSL certificates are generated correctly
   - Security hardening is applied
   - Redis and Memcached are running with proper authentication
   - FastAPI application is deployed and functional

## Knowledge Transfer Plan

1. Document each Ansible role with detailed README files
2. Create a migration report comparing Chef and Ansible implementations
3. Conduct a walkthrough session with the team
4. Create runbooks for common operations