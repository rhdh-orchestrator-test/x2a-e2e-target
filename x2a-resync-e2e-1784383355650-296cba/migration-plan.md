# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef deployment scripts and Ansible playbooks that need to be consolidated into a unified Ansible approach. The repository primarily consists of:

1. Chef Automate and Chef Infra Server deployment scripts (Bash)
2. Ansible playbooks for web server configuration with InSpec tests for compliance verification
3. Test Kitchen configuration for infrastructure testing

The migration complexity is relatively low as most of the repository already contains Ansible playbooks. The primary focus will be on replacing the Chef server deployment scripts with Ansible equivalents and ensuring the InSpec tests continue to work with the migrated infrastructure. Estimated timeline: 1-2 weeks for a complete migration.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for configuring HTTPS websites with InSpec compliance tests
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL/TLS security hardening, compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec verification. Migration should replace this with Ansible-native testing solutions like Molecule.
- `chef-and-ansible/website_https.yml`: Ansible playbook for configuring Apache with HTTPS. Can be kept as-is or refactored into Ansible roles.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability. Can be kept as-is or integrated into the main Apache role.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS configuration. Can be kept as-is for compliance testing with Ansible.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Can be kept as-is for compliance testing with Ansible.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Should be replaced with Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Should be replaced with Ansible playbook.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and Apache package version in website_https.yml)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Keep using InSpec for compliance testing with Ansible. InSpec works well with Ansible and doesn't need replacement.
- **Test Kitchen**: Replace with Molecule for Ansible-native testing or adapt to use Ansible directly.
- **Chef Automate/Infra Server**: Replace with Ansible AWX/Tower or another Ansible management platform.

### Security Considerations

- **SSL/TLS Configuration**: The repository includes specific SSL hardening (disabling SSLv3, enabling TLSv1.2). Ensure these security configurations are maintained in the migrated Ansible roles.
- **SSH Security**: InSpec tests verify SSH root login is disabled. Ensure this security check is maintained.
- **Self-signed Certificates**: The current implementation uses self-signed certificates. Consider implementing proper certificate management in the Ansible migration.
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates and keys should be managed securely
  - Count: 2 credential sets detected (user login, SSL certificates)

### Technical Challenges

- **InSpec Integration**: Ensuring InSpec tests continue to work with the migrated Ansible infrastructure. Mitigation: Use Ansible's built-in support for InSpec or integrate via custom modules.
- **Chef Server Replacement**: Determining if Chef Server functionality needs to be replaced with Ansible Tower/AWX or if it can be eliminated entirely. Mitigation: Assess current usage of Chef Server and determine if Ansible Tower/AWX meets requirements.

### Migration Order

1. **Ansible Playbooks** (chef-and-ansible/website_https.yml, chef-and-ansible/poodle_fix.yml): Low risk, already in Ansible format. Refactor into roles for better organization.
2. **Testing Framework** (chef-and-ansible/kitchen.yml): Moderate complexity. Replace with Molecule or adapt to use Ansible directly.
3. **Chef Server Deployment** (setup-automate scripts): High complexity. Replace with Ansible playbooks for deploying Ansible management infrastructure.

### Assumptions

1. The InSpec tests are required for compliance verification and should be maintained.
2. The Chef Automate and Chef Infra Server deployment is needed for infrastructure management and should be replaced with equivalent Ansible management tools.
3. The target environment is Ubuntu 20.04 running on Vagrant VMs.
4. The hardcoded credentials in the setup scripts are for testing purposes only and will be replaced with secure credential management in production.
5. The self-signed certificates are for testing purposes only and will be replaced with proper certificate management in production.