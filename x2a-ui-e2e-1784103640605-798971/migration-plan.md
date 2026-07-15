# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mixed environment of Chef InSpec and Ansible configurations focused on compliance automation. The primary components are:

1. Ansible playbooks for configuring a secure HTTPS website
2. Chef InSpec tests for verifying compliance of the deployed configurations
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests. The estimated timeline for migration is 1-2 weeks, with low complexity for the Ansible components (which can be retained) and moderate complexity for replacing the InSpec testing framework with Ansible-native solutions.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook for deploying a secure HTTPS website with Apache2
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: SSL certificate generation, Apache2 configuration, virtual host setup

- **poodle-fix**:
    - Description: Ansible playbook for remediating SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website-https-verify**:
    - Description: Chef InSpec test for verifying HTTPS website functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh-profile**:
    - Description: Chef InSpec control for verifying SSH root login is disabled (STIG compliance)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, STIG compliance check, security tagging

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file for the website deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Replace InSpec tests with equivalent Ansible assert modules
  - Consider using ansible-lint for static analysis
  - Implement Molecule for test-driven development
  - Use ansible-test for integration testing

- **Test Kitchen**: Replace with Molecule for Ansible role testing:
  - Molecule provides similar functionality for testing Ansible roles
  - Can use the same Vagrant driver for local testing

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks:
  - Create Ansible roles for configuration management
  - Consider using AWX/Ansible Tower for web UI and job scheduling

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook:
  - Ensure TLSv1.2 remains enabled and older protocols disabled
  - Maintain proper certificate generation and management

- **SSH Hardening**: The SSH security controls tested by ssh_profile.rb must be implemented:
  - Ensure PermitRootLogin is properly configured
  - Maintain STIG compliance requirements

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates should be managed securely
  - Count of credentials detected: 3 (username, password, and SSL certificates)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions:
  - Challenge: InSpec provides domain-specific language for compliance testing
  - Mitigation: Use Ansible assert module with custom scripts where needed, or maintain InSpec for testing only

- **Compliance Reporting**: Replacing Chef Automate compliance reporting:
  - Challenge: Chef Automate provides rich compliance reporting dashboards
  - Mitigation: Consider integrating with tools like Prometheus/Grafana or OpenSCAP for compliance reporting

- **Test Kitchen Workflow**: Replacing Test Kitchen testing workflow:
  - Challenge: Team may be familiar with Test Kitchen workflow
  - Mitigation: Provide documentation and training on Molecule testing workflow

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml):
   - Low risk as these are already in Ansible format
   - Refactor into proper Ansible roles with variables
   - Remove hardcoded values and improve idempotence

2. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh):
   - Convert bash scripts to Ansible playbooks
   - Implement proper variable management with Ansible Vault
   - Create roles for Chef server deployment if still needed

3. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb):
   - Highest complexity due to framework change
   - Convert to Ansible assertions or maintain as InSpec tests
   - Ensure compliance requirements are still met

### Assumptions

1. The primary goal is to standardize on Ansible and remove Chef dependencies
2. The team has Ansible expertise or will receive training
3. Compliance testing and reporting are still requirements
4. The deployment scripts for Chef Automate/Infra Server may no longer be needed if fully migrating to Ansible
5. The target environment will remain Ubuntu 20.04 on Vagrant VMs
6. The security requirements (STIG compliance, SSL hardening) must be maintained
7. The current repository is a demonstration/example and not a production system
8. Test Kitchen is used for development workflow and will need a replacement