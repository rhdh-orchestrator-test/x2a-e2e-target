# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are bash scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible components are already in place. The main migration effort will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Migrating Chef Automate/Infra Server deployment scripts to Ansible playbooks

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
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that ensures SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

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
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis

- **Test Kitchen**: Replace with Molecule for Ansible-native testing framework

- **Chef Automate/Infra Server**: Replace with:
  - AWX/Ansible Tower for orchestration
  - Ansible content collections for configuration management
  - GitLab CI/GitHub Actions for pipeline automation

### Security Considerations

- **SSL Configuration**: The current implementation fixes POODLE vulnerability by enforcing TLSv1.2. Ensure this security hardening is maintained in the migrated solution.
  - Migration approach: Preserve the same Apache SSL configuration in the Ansible playbook

- **SSH Security**: The InSpec test checks for disabled root SSH login. Ensure this compliance check is maintained.
  - Migration approach: Convert the InSpec control to an Ansible assert or use ansible-lint security rules

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates are generated on the fly, which is acceptable for testing but should use proper certificate management for production

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach may require additional logic.
  - Mitigation: Use Ansible's assert module with careful condition crafting or consider maintaining InSpec for testing if it integrates well with your workflow.

- **Chef Automate Functionality**: Chef Automate provides compliance reporting that needs an equivalent in the Ansible ecosystem.
  - Mitigation: Consider AWX/Tower with custom reporting or integrate with compliance tools like OpenSCAP.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format, just need review and potential refactoring
2. **Bash Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Medium complexity, convert to Ansible roles
3. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Higher complexity, convert to Ansible testing framework

### Assumptions

1. The primary purpose of this repository is demonstration/educational rather than production use
2. The InSpec tests are intended to validate the Ansible-deployed configurations
3. The hardcoded credentials in the deployment scripts are for demonstration purposes only
4. The self-signed certificates are acceptable for the demonstration environment
5. The target environment is Ubuntu 20.04 running on Vagrant VMs
6. There are no external dependencies or integrations beyond what's visible in the repository
7. The migration will maintain the same level of security compliance checking
8. The current setup doesn't use encrypted secrets or have complex authentication requirements