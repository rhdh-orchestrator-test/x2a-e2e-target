# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef deployment scripts and Ansible playbooks with Chef InSpec testing. The migration scope is relatively small, with two main components that need to be consolidated into a pure Ansible solution:

1. Chef Automate and Chef Infra Server deployment scripts (currently in Bash)
2. Ansible playbooks with Chef InSpec testing for compliance automation

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on converting the Chef Automate deployment scripts to Ansible playbooks and ensuring the existing Ansible playbooks are properly integrated into the new structure.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks with Chef InSpec testing for compliance automation
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL security hardening, InSpec compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration should include converting to Ansible Molecule for testing.
- `chef-and-ansible/website_https.yml`: Ansible playbook for configuring Apache with HTTPS. Can be directly incorporated into the Ansible structure.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities. Can be directly incorporated into the Ansible structure.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS configuration. Should be converted to Ansible testing framework or kept as InSpec tests.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance. Should be converted to Ansible testing framework or kept as InSpec tests.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Needs to be converted to Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Needs to be converted to Ansible playbook.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and Apache package version in website_https.yml)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Currently used for compliance testing. Options:
  1. Keep InSpec for testing and integrate with Ansible
  2. Replace with Ansible-native testing solutions like Molecule with TestInfra
  3. Use Ansible's assert module for basic testing

- **Test Kitchen**: Currently used for testing Ansible playbooks. Replace with Ansible Molecule for testing.

- **Chef Automate/Infra Server**: The deployment scripts need to be replaced with Ansible playbooks that can deploy alternative infrastructure management solutions:
  1. Ansible AWX/Tower as a replacement for Chef Automate
  2. GitLab CI/CD or Jenkins for pipeline automation
  3. Compliance automation using OpenSCAP or continue using InSpec

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL and fix POODLE vulnerability. Migration must maintain these security hardening measures.
  - Migration approach: Preserve the SSL configuration tasks in the Ansible playbooks.

- **SSH Hardening**: InSpec tests verify SSH root login is disabled. Migration must ensure this security check is maintained.
  - Migration approach: Convert InSpec SSH tests to Ansible assert tasks or maintain InSpec tests.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts: The Chef deployment scripts contain hardcoded usernames and passwords that should be moved to Ansible Vault.
  - SSL certificates: Self-signed certificates are generated in the Ansible playbook. Consider using Let's Encrypt for production environments.
  - Count of credentials detected:
    - setup-automate: 3 credentials (username, password, organization name)

### Technical Challenges

- **Chef InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing may require additional effort to maintain the same level of compliance verification.
  - Mitigation strategy: Consider keeping InSpec as a testing tool and integrating it with Ansible, or invest time in developing equivalent tests with Ansible's testing frameworks.

- **Chef Automate Replacement**: Determining the appropriate replacement for Chef Automate functionality within an Ansible ecosystem.
  - Mitigation strategy: Evaluate Ansible AWX/Tower as a replacement and develop playbooks for its deployment and configuration.

### Migration Order

1. **chef-and-ansible** (low risk, high value): The existing Ansible playbooks can be directly incorporated into the new structure with minimal changes.
2. **setup-automate** (moderate complexity): Convert the Chef deployment scripts to Ansible playbooks for deploying alternative infrastructure management solutions.

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production, as indicated by the README.md mentioning "working examples" and "how-tos".
2. The Chef Automate and Chef Infra Server deployment scripts are used for setting up test environments rather than production environments, given the hardcoded credentials.
3. The target environment is Ubuntu 20.04 based on the kitchen.yml configuration.
4. The migration will need to address the replacement of Chef Automate and Chef Infra Server with equivalent Ansible-based solutions.
5. The InSpec tests are valuable for compliance verification and should either be maintained or replaced with equivalent functionality.
6. The current setup uses Vagrant for local testing, which can be maintained or replaced with other virtualization technologies.