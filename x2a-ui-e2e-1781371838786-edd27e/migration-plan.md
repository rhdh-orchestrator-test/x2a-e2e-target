# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, with two main components: 1) Ansible playbooks with InSpec tests for compliance verification, and 2) Chef Automate/Chef Infra Server deployment scripts. The migration complexity is low to medium, with an estimated timeline of 1-2 weeks for a complete migration.

## Module Migration Plan

This repository contains Chef and Ansible components that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks with Chef InSpec tests for compliance verification of web servers
    - Path: chef-and-ansible/
    - Technology: Ansible with Chef InSpec
    - Key Features: HTTPS website deployment, SSL configuration, compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash scripts for Chef infrastructure
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration should replace with Ansible Molecule or maintain Kitchen for InSpec tests.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying HTTPS website. Can be directly used in Ansible migration.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability. Can be directly used in Ansible migration.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for HTTPS website verification. Can be maintained as-is for compliance testing.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance. Can be maintained as-is for compliance testing.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Should be replaced with Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Should be replaced with Ansible playbook.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and package versions in Ansible playbooks)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Maintain InSpec for compliance testing, integrate with Ansible using the `inspec` Ansible module or post-tasks
- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that perform equivalent setup

### Security Considerations

- **SSL Configuration**: The migration must maintain proper SSL configuration (TLSv1.2) as implemented in the poodle_fix.yml playbook
- **SSH Security**: Maintain SSH hardening compliance checks as defined in ssh_profile.rb
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates are generated dynamically in the playbooks, which is a good practice to maintain

### Technical Challenges

- **InSpec Integration**: Ensuring proper integration of InSpec tests with Ansible for compliance verification
  - Mitigation: Use the Ansible `inspec` module or maintain Test Kitchen for verification
- **Chef Automate Replacement**: Determining if Chef Automate functionality needs to be replaced
  - Mitigation: Evaluate if Ansible AWX/Tower can provide equivalent functionality or if Chef Automate should be maintained for compliance reporting

### Migration Order

1. Ansible playbooks (website_https.yml, poodle_fix.yml) - Low risk as they're already in Ansible format
2. InSpec test integration - Medium complexity to ensure proper integration with Ansible workflow
3. Chef Automate/Infra Server deployment scripts - Higher complexity, requires creating equivalent Ansible playbooks

### Assumptions

1. The repository is primarily for demonstration purposes rather than production use
2. InSpec will continue to be used for compliance testing even after migration
3. The Chef Automate/Infra Server deployment may be replaced entirely or partially depending on requirements
4. The target environment will remain Ubuntu 20.04 or compatible
5. The hardcoded credentials in the deployment scripts are for demonstration only and will be properly secured in the migration
6. The SSL configuration requirements (disabling SSLv3, enabling TLSv1.2) must be maintained in the migration