# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation and infrastructure deployment. The migration scope is relatively small, focusing on:

1. Converting Chef InSpec tests to Ansible-compatible testing frameworks
2. Consolidating existing Ansible playbooks into a more structured Ansible project
3. Migrating Chef server deployment scripts to Ansible playbooks

Given the limited scope and the fact that part of the infrastructure is already using Ansible, this migration is estimated to be of **low complexity** with an estimated timeline of **1-2 weeks**.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling older protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration compliance testing

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS is properly configured
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol verification

- **deploy-automate**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate deployment, Chef Server configuration, user and organization setup

- **deploy-chef-server**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server deployment, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration file that uses Ansible as the provisioner and InSpec as the verifier. Will need to be updated to use pure Ansible testing framework.
- `index.html`: Simple HTML file used for testing the web server deployment.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use the ansible-lint tool for static analysis

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Replace with:
  - AWX/Ansible Tower for orchestration
  - Ansible Collections for configuration management
  - GitLab CI/GitHub Actions for pipeline automation

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL configuration for Apache. Migration should maintain or improve the security posture:
  - Continue enforcing TLS 1.2+ only
  - Ensure proper certificate generation and management
  - Consider integrating with Let's Encrypt for production environments

- **SSH Hardening**: The InSpec tests verify SSH security configurations. Migration should:
  - Maintain SSH hardening checks
  - Implement equivalent controls in Ansible

- **Credential Management**: The Chef server deployment scripts contain hardcoded credentials:
  - Replace with Ansible Vault for secure credential storage
  - Implement proper secret management for user passwords
  - Document: 3 credential instances detected in deploy scripts (username, password, email)

### Technical Challenges

- **Testing Framework Migration**: Converting InSpec tests to Ansible-compatible testing:
  - Challenge: InSpec provides specific testing capabilities that may not have direct equivalents in Ansible
  - Mitigation: Use a combination of Ansible assert, custom modules, and external testing tools

- **Chef Server Functionality**: Replacing Chef Server functionality with Ansible equivalents:
  - Challenge: Chef Server provides specific organizational structures and authentication mechanisms
  - Mitigation: Design equivalent structures in Ansible Tower/AWX or implement custom solutions

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format, just need restructuring
2. **InSpec Tests** (ssh_profile.rb, website_https_verify.rb): Moderate complexity to convert to Ansible testing framework
3. **Chef Server Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Highest complexity, requires designing equivalent Ansible roles

### Assumptions

1. The repository is primarily used for demonstration/educational purposes rather than production, based on the simple examples and documentation references.
2. The InSpec tests are used for validating configurations managed by Ansible, not as part of a larger Chef ecosystem.
3. The Chef server deployment scripts are examples and not part of the core functionality being tested.
4. The target environment is Ubuntu 20.04 running on Vagrant VMs.
5. No complex data structures or external integrations are present beyond what's visible in the code.
6. The migration will maintain the same level of security validation currently provided by InSpec tests.