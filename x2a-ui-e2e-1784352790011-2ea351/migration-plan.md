# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations that need to be consolidated into a unified Ansible approach. The repository primarily consists of:

1. Chef Automate and Chef Infra Server deployment scripts
2. Ansible playbooks for configuring HTTPS websites with Apache
3. Chef InSpec tests for compliance verification

The migration complexity is relatively low as most of the configuration is already in Ansible format. The primary focus will be on replacing the Chef Automate/Infra Server deployment scripts with Ansible equivalents and ensuring the InSpec tests can be integrated into an Ansible-based workflow. Estimated timeline: 1-2 weeks.

## Module Migration Plan

This repository contains Chef and Ansible configurations that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for configuring HTTPS websites with Apache and InSpec tests for compliance verification
    - Path: chef-and-ansible
    - Technology: Ansible + Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL/TLS security settings, InSpec compliance tests

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash + Chef
    - Key Features: Chef Automate deployment, Chef Infra Server configuration, user and organization setup

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook that configures Apache with HTTPS support. Migration considerations include preserving the SSL certificate generation and virtual host configuration.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook that addresses SSL POODLE vulnerability by enforcing TLSv1.2. Migration considerations include ensuring this security fix is maintained.
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec. Migration considerations include replacing with Ansible-native testing solutions or adapting to work with pure Ansible.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality. Migration considerations include converting to Ansible test framework or maintaining InSpec integration.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Migration considerations include converting to Ansible test framework or maintaining InSpec integration.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate. Migration considerations include replacing with Ansible playbook for infrastructure management.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Migration considerations include replacing with Ansible playbook for infrastructure management.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and apt package management in playbooks)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver configuration)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server CLI**: Replace with Ansible roles for configuration management
- **InSpec**: Consider options:
  1. Maintain InSpec for compliance testing and integrate with Ansible workflow
  2. Replace with Ansible-native testing frameworks like Molecule or ansible-test
  3. Use community modules like `geerlingguy.inspec` to run InSpec from Ansible

### Security Considerations

- **SSL/TLS Configuration**: The repository includes specific security fixes (POODLE vulnerability mitigation) that must be preserved in the migration.
  - Migration approach: Ensure the Ansible playbooks maintain the same security settings for SSL/TLS.

- **SSH Security**: InSpec tests verify SSH root login is disabled.
  - Migration approach: Ensure Ansible playbooks configure SSH with the same security settings and include verification.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Self-signed SSL certificates generated in playbooks
  - Migration approach: Replace hardcoded credentials with Ansible Vault and implement proper certificate management.

### Technical Challenges

- **InSpec Integration**: Determining the best approach for maintaining compliance testing with InSpec or migrating to Ansible-native testing.
  - Mitigation strategy: Evaluate ansible-test, Molecule, and other testing frameworks against current InSpec capabilities.

- **Chef Automate Replacement**: Identifying Ansible equivalents for Chef Automate functionality.
  - Mitigation strategy: Evaluate AWX/Tower or other Ansible management platforms to replace Chef Automate functionality.

### Migration Order

1. **chef-and-ansible/website_https.yml and poodle_fix.yml** (low risk, already in Ansible format)
2. **InSpec tests** (moderate complexity, requires decision on testing strategy)
3. **setup-automate scripts** (high complexity, requires architectural decisions on Ansible management)

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being production infrastructure code.
2. The Chef Automate and Chef Infra Server deployment scripts are used for setting up test environments.
3. The hardcoded credentials in the deployment scripts are not used in production environments.
4. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.
5. The self-signed certificates in the Ansible playbooks are acceptable for the use case and not intended for production use.
6. The InSpec tests are valuable and should be preserved in some form rather than eliminated.
7. The migration will not require significant changes to the underlying infrastructure or application architecture.