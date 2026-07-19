# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that demonstrate compliance automation. The primary focus is on using Chef InSpec for compliance testing alongside Ansible for configuration management. Additionally, there are Chef Automate and Chef Infra Server setup scripts. The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Demonstration of using Chef InSpec with Ansible for compliance automation
    - Path: chef-and-ansible
    - Technology: Mixed (Ansible playbooks and Chef InSpec tests)
    - Key Features: HTTPS website deployment, SSL configuration, compliance testing

- **setup-automate**:
    - Description: Scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible Molecule for testing.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure website. Migration consideration: Can be directly used in Ansible.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities. Migration consideration: Can be directly used in Ansible.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality. Migration consideration: Convert to Ansible assertions or molecule tests.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Migration consideration: Convert to Ansible assertions or molecule tests.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Migration consideration: Replace with Ansible role for infrastructure setup.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Migration consideration: Replace with Ansible role for infrastructure setup.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with ansible-lint for static analysis
  - Option 3: Use Ansible's built-in testing framework for more complex tests

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper SSL configuration is maintained during migration.
  - Migration approach: Preserve the same SSL configuration parameters in the Ansible roles.

- **SSH Security**: InSpec tests verify SSH root login is disabled.
  - Migration approach: Create equivalent Ansible assertions or use ansible-lint rules.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage
  - Count of credentials detected: 4 (username, longusername, useremail, userpassword) in setup-automate scripts

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing mechanisms.
  - Mitigation: Use Ansible assert module for simple tests, consider ansible-lint for more complex compliance checks.

- **Chef Automate Replacement**: Determining the appropriate Ansible-based alternative for Chef Automate functionality.
  - Mitigation: Consider AWX/Ansible Tower or other Ansible-compatible compliance and automation platforms.

### Migration Order

1. Ansible Playbooks (website_https.yml, poodle_fix.yml) - Low risk, already in Ansible format
2. InSpec Tests (website_https_verify.rb, ssh_profile.rb) - Moderate complexity, requires conversion to Ansible testing format
3. Chef Automate Setup Scripts - Higher complexity, requires replacement with Ansible roles

### Assumptions

1. The primary goal is to consolidate on Ansible and remove Chef dependencies.
2. The InSpec tests are used primarily for compliance verification and can be replaced with Ansible's testing capabilities.
3. The deployment scripts for Chef Automate and Chef Infra Server will be replaced with equivalent Ansible roles.
4. The target environment will remain Ubuntu 20.04 or compatible Linux distributions.
5. Vagrant will continue to be used for development/testing environments.
6. No external services or APIs are being called that would require special handling.
7. The hardcoded credentials in the setup scripts are for demonstration purposes and will be properly secured in the migrated solution.
8. The repository is primarily for demonstration purposes as indicated in the README.md, showing how Chef InSpec can be used alongside Ansible.