# MIGRATION FROM CHEF INSPEC TO ANSIBLE

## Executive Summary

This repository contains examples of using Chef InSpec alongside Ansible for compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions. The repository primarily demonstrates how to use Chef InSpec for compliance testing with Ansible playbooks rather than containing full Chef cookbooks that need migration.

The estimated timeline for migration is 1-2 weeks, with low complexity as the repository contains only InSpec test profiles and Ansible playbooks that are already in place. The main effort will be replacing InSpec tests with Ansible-native testing solutions.

## Module Migration Plan

This repository contains Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https_verify**:
    - Description: InSpec tests for verifying HTTPS website configuration including port listening, content verification, and SSL/TLS protocol checks
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port verification, HTTP response testing, SSL/TLS protocol validation

- **ssh_profile**:
    - Description: InSpec compliance profile for SSH security configuration focusing on root login restrictions
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, CCI compliance checks, STIG validation

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook that sets up an Apache web server with HTTPS support. Migration considerations include ensuring the playbook works with new testing framework.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability. Migration considerations include ensuring the playbook works with new testing framework.
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be updated to use Ansible-native testing solution.
- `setup-automate/deploy-automate.sh`: Script for deploying Chef Automate and Chef Infra Server. Will need to be replaced with Ansible playbook for infrastructure setup.
- `setup-automate/deploy-chef-server.sh`: Script for deploying Chef Infra Server. Will need to be replaced with Ansible playbook for infrastructure setup.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM setup

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions such as:
  - **Molecule**: For Ansible role testing
  - **ansible-lint**: For linting Ansible playbooks
  - **ansible-test**: For testing Ansible collections
  - **pytest-ansible**: For Python-based testing of Ansible playbooks

- **Test Kitchen**: Replace with Molecule for testing Ansible roles and playbooks

### Security Considerations

- **SSH root login restrictions**: The SSH profile tests for disabled root login. Ensure this security check is maintained in the Ansible-native testing solution.
- **SSL/TLS protocol security**: The website_https_verify tests check for disabled SSLv3 and enabled TLSv1.2. Ensure these security checks are maintained in the Ansible-native testing solution.
- **Vault/secrets management**: 
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificate handling should use Ansible's certificate management modules

### Technical Challenges

- **Compliance Testing Framework**: Chef InSpec provides a domain-specific language for compliance testing. Finding an equivalent in the Ansible ecosystem that provides the same level of expressiveness and compliance reporting may be challenging. Consider using a combination of Ansible assert modules and custom Python scripts.

- **Test Kitchen Integration**: The current setup uses Test Kitchen to orchestrate Ansible playbook execution and InSpec testing. Replacing this with Molecule will require reconfiguring the test workflow.

### Migration Order

1. **Ansible Playbooks** (already in place, no migration needed)
2. **InSpec Tests** (convert to Ansible-native testing solutions)
   - Start with website_https_verify.rb (simpler tests)
   - Then migrate ssh_profile.rb (more complex compliance tests)
3. **Setup Scripts** (convert to Ansible playbooks)
   - deploy-chef-server.sh
   - deploy-automate.sh

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, not to provide full Chef cookbooks.
2. The InSpec tests are used for compliance validation rather than functional testing of the Ansible playbooks.
3. The target environment is Ubuntu 20.04 running on Vagrant VMs.
4. The setup scripts are used for demonstration purposes and not for production deployments.
5. There are no external dependencies or complex Chef cookbooks that need migration.
6. The repository is primarily educational/demonstrative rather than a production codebase.
7. The hardcoded credentials in the setup scripts are for demonstration purposes only.