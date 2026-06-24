# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together for compliance automation. The primary focus appears to be demonstrating how Chef InSpec can be used alongside Ansible for continuous compliance validation. Additionally, there are Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with most components already in Ansible format. The estimated timeline for complete migration is 1-2 weeks, with low complexity for the Ansible playbooks (already in place) and moderate complexity for converting the InSpec tests to Ansible-native solutions.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling older protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Simple HTML file used as a test page for the web server

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic compliance checks
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks

- **Test Kitchen**: Replace with Molecule for Ansible playbook testing
  - Molecule provides similar functionality but is designed specifically for Ansible

- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform
  - Migrate user and organization management to AAP
  - Set up project structures in AAP that mirror the Chef organization structure

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL configuration for Apache. Ensure these security settings are preserved in the migrated Ansible playbooks.
  - Migration approach: Maintain the same SSL protocol restrictions (TLSv1.2) in the Ansible tasks

- **SSH Security**: The InSpec tests verify SSH root login is disabled. Ensure this security check is maintained.
  - Migration approach: Create an Ansible task that verifies the SSH configuration using the `lineinfile` module with `state: absent` for checking that `PermitRootLogin yes` is not present

- **Vault/secrets management**: 
  - Hardcoded credentials in setup scripts: The deploy-automate.sh and deploy-chef-server.sh scripts contain hardcoded passwords
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing solutions
  - Mitigation strategy: Use Ansible's assert module for basic tests, and consider ansible-lint for more complex compliance checks

- **Compliance Reporting**: InSpec provides detailed compliance reporting that may not be directly available in Ansible
  - Mitigation strategy: Consider integrating with Ansible Automation Platform's compliance capabilities or use a third-party compliance tool that integrates with Ansible

### Migration Order

1. Ansible Playbooks (website_https.yml, poodle_fix.yml) - low risk, already in Ansible format
2. Bash Deployment Scripts (deploy-automate.sh, deploy-chef-server.sh) - moderate complexity
3. InSpec Tests (website_https_verify.rb, ssh_profile.rb) - high complexity, requires alternative testing approach

### Assumptions

1. The primary goal is to move all functionality to Ansible, including testing capabilities currently provided by InSpec
2. The target environment will continue to be Ubuntu 20.04 running on Vagrant VMs
3. The security compliance requirements (STIG references in ssh_profile.rb) will need to be maintained in the Ansible solution
4. The Chef Automate and Chef Infra Server deployment scripts are intended to be replaced with equivalent Ansible playbooks for setting up Ansible Automation Platform
5. No external data sources or databases are being used that would require additional migration steps
6. The current implementation is primarily for demonstration/testing purposes rather than production use
7. The hardcoded credentials in the deployment scripts are not used in production environments