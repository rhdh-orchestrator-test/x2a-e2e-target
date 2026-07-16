# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are bash scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible components are already in place. The main migration effort will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Migrating Chef Automate/Infra Server deployment scripts to Ansible playbooks
3. Ensuring all compliance checks are properly implemented in the Ansible ecosystem

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
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
    - Description: Chef InSpec test that verifies SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance with security standards (STIG)

- **chef-automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Simple HTML file used as a test page for the web server

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM setup

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic compliance checks
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks
  - Option 4: Consider integrating with OpenSCAP for advanced compliance testing

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Consider using ansible-test for collections testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Automation Platform (AAP) for enterprise automation
  - AWX (open-source version of Ansible Tower) for smaller deployments
  - GitLab CI/CD or Jenkins for CI/CD pipeline integration

### Security Considerations

- **SSL/TLS Configuration**: The current implementation properly disables SSLv3 and enables only TLSv1.2. This should be maintained in the migrated solution.
  - Migration approach: Use the same configuration in Ansible tasks, consider using the `community.crypto` collection for certificate management

- **SSH Security**: The InSpec test checks for disabled root login, which is a critical security control.
  - Migration approach: Implement equivalent checks using Ansible's assert module or integrate with OpenSCAP

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely, potentially using ansible-vault for private keys
  - Document the count and type of credentials detected per module:
    - chef-automate-deploy: 1 password (hardcoded)
    - chef-server-deploy: 1 password (hardcoded)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing solutions may require different approaches:
  - Challenge: InSpec provides a domain-specific language for compliance testing that is more expressive than Ansible's built-in testing capabilities
  - Mitigation: Use a combination of Ansible's assert module, custom modules, and integration with tools like OpenSCAP

- **Chef Automate Functionality**: Ensuring all necessary Chef Automate functionality is replicated in the Ansible ecosystem
  - Challenge: Chef Automate provides integrated compliance reporting that may need to be replicated
  - Mitigation: Implement equivalent functionality using Ansible Automation Platform or integrate with third-party compliance tools

### Migration Order

1. **website_https.yml and poodle_fix.yml** (low risk, already Ansible)
   - Review and optimize existing Ansible playbooks
   - Consolidate into a single role if appropriate

2. **InSpec Tests** (moderate complexity)
   - Convert website_https_verify.rb to Ansible assertions or Molecule tests
   - Convert ssh_profile.rb to Ansible assertions or integrate with OpenSCAP

3. **Chef Deployment Scripts** (high complexity)
   - Create Ansible playbooks to replace deploy-automate.sh and deploy-chef-server.sh
   - Implement secure credential management using Ansible Vault

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance testing, not for production deployment.
2. The target environment is Ubuntu 20.04 running on Vagrant VMs.
3. The security requirements (SSL/TLS configuration, SSH security) are critical and must be maintained in the migrated solution.
4. There are no external dependencies or integrations beyond what is visible in the repository.
5. The Chef Automate and Chef Infra Server deployment scripts are used for demonstration purposes and not for production deployments.
6. No custom Chef resources or complex Chef-specific functionality is being used that would require special handling during migration.
7. The migration will be to pure Ansible without maintaining any Chef components.