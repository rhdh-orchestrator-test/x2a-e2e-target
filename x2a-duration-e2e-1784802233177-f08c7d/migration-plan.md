# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus is on using Chef InSpec for compliance testing alongside Ansible for configuration management. The repository also includes setup scripts for Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible components are already in place. The main migration effort will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Updating the Chef Automate and Chef Infra Server setup scripts to Ansible playbooks
3. Ensuring the existing Ansible playbooks follow best practices

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that checks SSH configuration for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance tagging (STIG, CCI)

- **deploy-automate**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: System configuration, Chef Automate installation, user and organization setup

- **deploy-chef-server**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: System configuration, Chef Infra Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be updated to use Ansible-native testing solutions.
- `index.html`: Simple HTML file used as a test page for the web server.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis

- **Test Kitchen**: Replace with:
  - Option 1: Molecule for Ansible role testing
  - Option 2: Ansible's built-in testing capabilities

- **Chef Automate/Infra Server**: Replace with:
  - Option 1: AWX/Ansible Tower for enterprise management
  - Option 2: Ansible Automation Platform

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper SSL/TLS protocols are enforced in the migrated solution.
  - Migration approach: Maintain the same SSL configuration but update to use Ansible's `apache2_module` module instead of commands.

- **SSH Security**: The InSpec tests check for SSH root login configuration. Ensure this security check is maintained.
  - Migration approach: Convert the InSpec test to an Ansible playbook that checks and enforces the same SSH configuration.

- **Self-signed Certificates**: The playbook generates self-signed certificates. Consider using Let's Encrypt for production.
  - Migration approach: Update the certificate generation to use Ansible's `acme_certificate` module for Let's Encrypt integration.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Move credentials to Ansible Vault

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions or Molecule tests.
  - Mitigation: Create a mapping of InSpec resources to Ansible modules and assertions.

- **Compliance Reporting**: InSpec provides rich compliance reporting that needs to be replicated.
  - Mitigation: Integrate with Ansible Tower/AWX for compliance reporting or use a dedicated compliance tool.

- **Test Kitchen Integration**: The current setup uses Test Kitchen to orchestrate testing.
  - Mitigation: Replace with Molecule or another Ansible-native testing framework.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format, just need to be updated to follow best practices.
2. **Bash Scripts** (deploy-automate.sh, deploy-chef-server.sh): Medium risk, need to be converted to Ansible playbooks.
3. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): High risk, need to be converted to Ansible-native testing solutions.

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployment.
2. The InSpec tests are used for compliance verification after Ansible playbook execution.
3. The target environment is Ubuntu 20.04 running on Vagrant VMs.
4. The setup scripts are used for setting up a test environment rather than production.
5. No external dependencies or integrations beyond what's visible in the repository.
6. The migration will maintain the same functionality but using Ansible-native solutions.
7. No specific performance requirements are needed for the migrated solution.
8. The current implementation doesn't use any advanced Chef features that would be difficult to replicate in Ansible.