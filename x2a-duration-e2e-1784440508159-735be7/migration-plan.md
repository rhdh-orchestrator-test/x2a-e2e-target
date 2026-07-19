# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single engineer, including testing and documentation.
**Complexity**: Low to Medium - The repository primarily contains Ansible playbooks already, with the main migration effort focused on InSpec tests and deployment scripts.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Integration of Chef InSpec with Ansible for compliance testing
    - Path: chef-and-ansible
    - Technology: Chef InSpec and Ansible
    - Key Features: HTTPS website deployment, SSL/TLS compliance testing, SSH security compliance testing

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible integration with InSpec - needs to be replaced with Ansible-native testing framework configuration
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure HTTPS website - can be preserved as-is
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities - can be preserved as-is
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for HTTPS website - needs conversion to Ansible testing framework
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance - needs conversion to Ansible testing framework
- `chef-and-ansible/index.html`: Sample HTML file used for testing - can be preserved as-is
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate - needs conversion to Ansible playbook
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server - needs conversion to Ansible playbook

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Test Kitchen (latest)**: Replace with Ansible Molecule for testing
  - Migration strategy: Create equivalent Molecule scenario files that replicate the Test Kitchen functionality
  
- **Chef InSpec (latest)**: Replace with one of the following:
  - Ansible's built-in assert module for basic testing
  - ansible-lint for static analysis
  - Molecule with testinfra for infrastructure testing
  - Ansible's built-in `--check` mode with custom verification tasks
  
- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - GitLab CI/CD or Jenkins for pipeline automation
  - Ansible Vault for secrets management

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Migration approach: Preserve the existing Ansible tasks that enforce TLSv1.2
  
- **Self-signed Certificate Generation**: The website_https.yml playbook generates self-signed certificates
  - Migration approach: Preserve the existing Ansible OpenSSL tasks
  
- **SSH Security Hardening**: The ssh_profile.rb InSpec test verifies SSH root login is disabled
  - Migration approach: Convert to Ansible assert tasks or testinfra tests that verify the same security controls

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) - migrate to Ansible Vault
  - SSL/TLS certificate references in website_https.yml - maintain existing approach but consider using Ansible Vault for private keys

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible testing frameworks
  - Mitigation: Use Ansible's assert module for simple tests, and testinfra for more complex infrastructure testing
  
- **Chef Automate Functionality**: Replacing Chef Automate's compliance reporting
  - Mitigation: Implement Ansible AWX/Tower with custom reporting dashboards or integrate with third-party compliance tools

- **Test Kitchen Integration**: Replacing Test Kitchen with Ansible-native testing
  - Mitigation: Implement Molecule for Ansible role and playbook testing

### Migration Order

1. **Ansible Playbooks** (Low risk, already Ansible): Preserve website_https.yml and poodle_fix.yml as they are already Ansible playbooks
2. **InSpec Tests** (Medium complexity): Convert website_https_verify.rb and ssh_profile.rb to Ansible testing framework
3. **Chef Deployment Scripts** (High complexity): Convert deploy-automate.sh and deploy-chef-server.sh to Ansible playbooks
4. **Test Kitchen Configuration** (Medium complexity): Replace kitchen.yml with Molecule configuration

### Assumptions

1. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) are working correctly and don't require modification beyond testing framework integration.
2. The target environment will continue to be Ubuntu 20.04 or compatible systems.
3. The Chef Automate and Chef Infra Server deployment scripts are used for setting up test environments and not production systems.
4. The hardcoded credentials in the deployment scripts are for testing purposes only and will be replaced with secure credential management in the migrated solution.
5. The InSpec tests are currently being used for compliance verification and the same level of verification is required in the Ansible-native solution.
6. The migration does not require preserving compatibility with Chef InSpec, as the goal is to move entirely to Ansible-based solutions.
7. The existing Test Kitchen configuration is primarily used for testing the Ansible playbooks with InSpec verification, and this functionality needs to be preserved in the Ansible-native solution.