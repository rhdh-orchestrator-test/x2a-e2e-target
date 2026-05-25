# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing rather than being a full Chef cookbook implementation. Additionally, there are bash scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible playbooks are already in place. The main migration effort will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Replacing Chef Automate/Infra Server deployment scripts with Ansible playbooks

**Estimated Timeline**: 1-2 weeks for a single developer, with minimal complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **inspec_tests**:
    - Description: Chef InSpec tests for verifying HTTPS functionality and SSH security compliance
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: HTTPS verification, SSL protocol testing, SSH configuration compliance testing

- **chef_deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash
    - Key Features: Chef server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and verifying with InSpec. Will need to be replaced with Ansible-native testing framework.
- `index.html`: Simple HTML file used for testing the web server. Can be reused as-is.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic compliance testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks

- **Test Kitchen**: Replace with Molecule for Ansible playbook testing

- **Chef Automate/Infra Server**: Replace deployment scripts with:
  - Ansible playbooks for server provisioning
  - Consider AWX/Ansible Tower as an alternative to Chef Automate

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL configuration for Apache. Migration should maintain:
  - Disabling of vulnerable protocols (SSL3)
  - Enabling of secure protocols (TLSv1.2)
  - Self-signed certificate generation

- **SSH Security**: The InSpec tests verify SSH root login is disabled. Migration should:
  - Maintain SSH compliance testing
  - Ensure SSH hardening is properly implemented in Ansible

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates and keys should be managed securely

### Technical Challenges

- **Testing Framework Migration**: Converting InSpec tests to Ansible-native testing will require:
  - Understanding the compliance requirements being tested
  - Implementing equivalent tests using Ansible's testing capabilities
  - Ensuring the same level of reporting and documentation

- **Chef Server Deployment**: Replacing Chef server deployment with Ansible alternatives:
  - Determining if Chef server functionality is still needed
  - If needed, creating Ansible playbooks to deploy Chef server
  - If not needed, identifying Ansible-native alternatives for the functionality

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format. May need minor updates for best practices.
2. **Testing Framework**: Convert InSpec tests to Ansible-native testing solutions.
3. **Chef Deployment Scripts**: Replace with Ansible playbooks or alternative solutions.

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being a production deployment.
2. The Chef server deployment scripts are used for testing/demo purposes and not critical production infrastructure.
3. There are no external dependencies or integrations not visible in the repository.
4. The target environment will continue to be Ubuntu 20.04 or compatible systems.
5. There are no specific compliance requirements beyond what's tested in the InSpec profiles.
6. The hardcoded credentials in the deployment scripts are for demo purposes only and not used in production.