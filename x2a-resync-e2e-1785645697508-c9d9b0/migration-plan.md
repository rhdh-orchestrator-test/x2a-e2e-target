# MIGRATION FROM BASH/ANSIBLE TO ANSIBLE

This repository contains Bash scripts for Chef deployment and Ansible playbooks with InSpec tests. The migration scope is focused on converting all components to pure Ansible.

## Module Migration Plan

This repository contains Bash scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

No traditional modules (Puppet manifests/init.pp, Chef recipes/default.rb, or PowerShell .psd1 files) were found in this repository.

The repository contains:

- **website-https**:
    - Description: Ansible playbook for Apache HTTPS configuration
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificates, virtual hosts

- **poodle-fix**:
    - Description: Ansible playbook for SSL POODLE vulnerability remediation
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL hardening

- **chef-automate-deploy**:
    - Description: Bash script for Chef Automate deployment
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user/org creation

- **chef-server-deploy**:
    - Description: Bash script for Chef Infra Server deployment
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Server installation, user/org creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec HTTPS tests
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec SSH security tests

### Target Details

- **Operating System**: Ubuntu 20.04
- **Virtual Machine Technology**: Vagrant
- **Cloud Platform**: Not specified

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Maintain for compliance testing
- **Test Kitchen**: Update for pure Ansible
- **Apache 2.4.41**: Maintain version pinning

### Security Considerations

- **SSL/TLS Configuration**: Maintain TLSv1.2 requirement
- **Self-signed Certificates**: Consider Let's Encrypt for production
- **SSH Hardening**: Maintain SSH security checks
- **Vault/secrets management**: 
  - Hardcoded credentials in setup-automate scripts
  - Migrate to Ansible Vault

### Technical Challenges

- **Chef Automate Deployment**: Convert to Ansible playbooks
- **InSpec Integration**: Ensure tests work with Ansible

### Migration Order

1. **Existing Ansible Playbooks** (Low risk)
2. **Chef Automate Deployment** (Moderate complexity)
3. **Testing Framework** (Low risk)

### Assumptions

1. Repository is for demonstration purposes
2. InSpec tests will be maintained
3. Hardcoded credentials are for demonstration only
4. Target environment will remain Ubuntu-based
5. No complex state management required
6. Chef deployment scripts to be converted to Ansible