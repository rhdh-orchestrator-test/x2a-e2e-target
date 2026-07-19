# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec testing. The migration scope is relatively small, focusing on two main components:

1. Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks
2. Existing Ansible playbooks with Chef InSpec testing that need to be consolidated into a pure Ansible solution

The migration complexity is **LOW to MEDIUM** with an estimated timeline of 1-2 weeks for a single engineer, primarily due to the need to replace Chef InSpec testing with Ansible-native testing solutions.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for deploying and securing a web server with Chef InSpec testing
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: HTTPS website deployment, SSL/TLS security configuration, compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration considerations include replacing with Ansible Molecule for testing.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure web server. Can be directly used in the Ansible migration with minor updates.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities. Can be directly used in the Ansible migration with minor updates.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality. Needs to be replaced with Ansible-native testing.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Needs to be replaced with Ansible-native testing.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Needs to be converted to an Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Needs to be converted to an Ansible playbook.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic testing
  - Option 2: Implement Ansible Molecule for comprehensive testing
  - Option 3: Use ansible-lint for static analysis and compliance checks

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace with:
  - Option 1: AWX/Ansible Tower for enterprise automation platform
  - Option 2: Ansible Semaphore for lightweight GUI
  - Option 3: GitLab CI/CD with Ansible for automation workflow

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable insecure protocols. Migration should maintain or enhance these security settings.
  - Migration approach: Preserve the existing SSL/TLS configurations in the Ansible playbooks.

- **SSH Security**: InSpec tests verify SSH root login is disabled.
  - Migration approach: Implement equivalent checks using Ansible's `assert` module or ansible-lint.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault.
  - SSL certificates are generated dynamically in the playbook, which is a good practice to maintain.
  - Count of credentials detected:
    - setup-automate: 3 credentials (username, password, organization name)
    - chef-and-ansible: 0 hardcoded credentials (certificates generated dynamically)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing solutions.
  - Mitigation strategy: Use Ansible's `uri` module for HTTP/HTTPS testing and `assert` module for validation. For more complex compliance testing, consider ansible-lint or OpenSCAP integration.

- **Chef Automate Functionality**: Ensuring all Chef Automate functionality is properly replaced.
  - Mitigation strategy: Clearly define which Chef Automate features are actually being used and map them to equivalent Ansible solutions (AWX/Tower, GitLab CI/CD, etc.).

### Migration Order

1. **chef-and-ansible Ansible Playbooks** (low risk, high value)
   - These are already Ansible playbooks and only need minor updates and testing framework changes.

2. **setup-automate Bash Scripts** (moderate complexity)
   - Convert these scripts to Ansible playbooks, replacing Chef Automate/Infra Server with appropriate Ansible management solutions.

### Assumptions

1. The primary purpose of the Chef InSpec tests is for compliance validation of the deployed infrastructure, not for continuous compliance monitoring.

2. The Chef Automate and Chef Infra Server deployment scripts are used for setting up a management environment, which will be replaced by an Ansible-based management solution.

3. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.

4. The existing Ansible playbooks are functional and follow best practices, requiring minimal changes beyond testing framework updates.

5. There are no external dependencies or integrations not visible in the provided repository files.

6. The hardcoded credentials in the setup scripts are for demonstration purposes and will be properly secured in the migrated solution.