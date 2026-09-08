# MIGRATION FROM CHEF EXAMPLES TO ANSIBLE

This repository contains Chef-related examples and deployment scripts rather than production Chef cookbooks requiring migration. The primary content consists of Ansible playbooks demonstrating Chef InSpec integration, deployment scripts for Chef infrastructure, and test examples. The migration scope is minimal as most content is already Ansible-based or consists of deployment utilities.

## Module Migration Plan

This repository contains demonstration and deployment content rather than traditional Chef cookbooks:

### MODULE INVENTORY

**No Chef cookbooks or recipes found for migration.** The repository contains:

- **website_https**: 
    - Description: Ansible playbook demonstrating Apache HTTPS configuration with self-signed certificates, SSL/TLS security hardening, and virtual host setup
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible (already migrated)
    - Key Features: OpenSSL certificate generation, Apache virtual host configuration, SSL protocol enforcement

- **poodle_fix**:
    - Description: Ansible playbook for SSL/TLS security hardening, specifically addressing POODLE vulnerability by enforcing TLS 1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible (already migrated)
    - Key Features: Apache SSL protocol configuration, TLS version enforcement

### Infrastructure Files

- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script with user and organization provisioning
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec compliance tests for HTTPS functionality and SSL/TLS configuration
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec security profile for SSH root login compliance (STIG-based controls)
- `chef-and-ansible/index.html`: Static HTML test content for web server verification

### Target Details

Based on the Ansible playbooks and test configurations:

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from kitchen.yml driver configuration)
- **Cloud Platform**: Not specified - designed for on-premises or cloud-agnostic deployment

## Migration Approach

### Key Dependencies to Address

**No external Chef dependencies identified** - the repository uses:
- **Test Kitchen with Ansible provisioner**: Already configured for Ansible workflow
- **Chef InSpec**: Compliance testing framework that integrates with Ansible (no migration needed)
- **OpenSSL Ansible modules**: Native Ansible cryptography modules already in use

### Security Considerations

The existing Ansible playbooks demonstrate good security practices:
- **SSL/TLS Configuration**: Self-signed certificate generation with proper key management, TLS 1.2 enforcement, POODLE vulnerability mitigation
- **File Permissions**: Appropriate file modes for certificates (0640) and web content (0644/0755)
- **Service Hardening**: SSH root login restrictions, Apache security configurations
- **Compliance Testing**: InSpec profiles for STIG-based security controls (V-38607, RHEL-08-000227)

**Vault/secrets management**: 
- Hardcoded credentials present in deployment scripts (userpassword='password')
- Certificate private keys generated on target systems
- No encrypted data bags or vault usage detected

### Technical Challenges

**Minimal migration complexity** due to existing Ansible implementation:
- **InSpec Integration**: The repository demonstrates Chef InSpec working alongside Ansible - this pattern can continue
- **Test Kitchen Workflow**: Existing kitchen.yml already configured for Ansible provisioner
- **Deployment Scripts**: Bash scripts for Chef infrastructure deployment are independent utilities

### Migration Order

**No traditional migration required** - content is already Ansible-based or consists of deployment utilities:

1. **Immediate Use**: Ansible playbooks (website_https.yml, poodle_fix.yml) are production-ready
2. **Security Review**: Update hardcoded credentials in deployment scripts
3. **Documentation**: Enhance README files with usage instructions and security considerations

### Assumptions

- This repository serves as an example/demonstration rather than production infrastructure code
- The Chef deployment scripts are intended for lab/development environments (evidenced by 'chef.lab' hostnames and simple passwords)
- InSpec compliance testing will continue alongside Ansible automation
- Test Kitchen with Ansible provisioner workflow will be maintained
- The target audience includes teams evaluating Chef InSpec integration with Ansible
- Ubuntu 20.04 platform choice reflects the demonstration environment rather than production requirements
- Self-signed certificates are acceptable for the demonstration use case
- The repository represents a "how-to" guide rather than infrastructure requiring migration