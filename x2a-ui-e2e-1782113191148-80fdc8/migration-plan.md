# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are bash scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible components are already in place. The main migration effort will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Replacing Chef Automate/Infra Server deployment scripts with Ansible playbooks
3. Ensuring all compliance checks are preserved in the new implementation

Estimated timeline: 1-2 weeks for a small team (1-2 engineers)

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that ensures SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file for testing web server functionality

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic compliance checks
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks

- **Test Kitchen**: Replace with Molecule for Ansible playbook testing
  - Molecule provides similar functionality but is more Ansible-native

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Tower/AWX for orchestration and job scheduling
  - Ansible Content Collections for role and module management
  - Git repositories for version control of Ansible content

### Security Considerations

- **SSL Configuration**: The current implementation properly disables SSLv3 and enables only TLSv1.2. This security practice should be preserved in the migrated solution.
  - Migration approach: Maintain the same SSL configuration in the Ansible playbook

- **SSH Security**: The InSpec test checks for disabled root login via SSH, which is a critical security control.
  - Migration approach: Convert the InSpec test to an Ansible assert or Molecule test

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing solutions may require different approaches for different test types.
  - Mitigation: Use a combination of Ansible's assert module, Molecule, and ansible-lint to cover all test scenarios

- **Compliance Reporting**: InSpec provides rich compliance reporting that may not be directly available in Ansible.
  - Mitigation: Integrate with additional tools like OpenSCAP or Compliance as Code frameworks

- **Chef Server Deployment**: The current deployment scripts for Chef Server need to be completely rewritten as Ansible playbooks.
  - Mitigation: Create Ansible roles for deploying Ansible Tower/AWX instead of Chef Server

### Migration Order

1. **website_https.yml** and **poodle_fix.yml** (low risk, already Ansible)
   - Review and optimize existing Ansible playbooks
   - Combine into a single role with appropriate tags

2. **InSpec Tests** (moderate complexity)
   - Convert website_https_verify.rb to Ansible/Molecule tests
   - Convert ssh_profile.rb to Ansible/Molecule tests

3. **Chef Server Deployment Scripts** (high complexity)
   - Create Ansible playbooks to deploy Ansible Tower/AWX
   - Implement secure credential management with Ansible Vault

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can work alongside Ansible for compliance automation, not for production deployment.

2. The hardcoded credentials in the deployment scripts are for demonstration purposes only and would be replaced with secure alternatives in a production environment.

3. The Test Kitchen configuration is used for development and testing, not for production deployments.

4. The SSL certificates generated are self-signed and for testing purposes only.

5. The target environment is Ubuntu 20.04, and the migration will maintain this target OS.

6. There are no external dependencies or integrations beyond what is explicitly shown in the repository.

7. The migration will focus on preserving the functionality and security controls demonstrated in the original repository.