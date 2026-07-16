# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. The repository also contains shell scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible components are already in place. The main migration effort will involve converting the Chef InSpec tests to Ansible-native testing solutions and replacing the Chef Automate/Infra Server deployment scripts with Ansible playbooks. The estimated timeline for this migration is 1-2 weeks, with low complexity.

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
    - Key Features: Port listening check, HTTPS response verification, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that ensures SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration verification, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Shell script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Shell script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Simple HTML file used as a test page for the web server

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - For basic tests: Use Ansible assert module
  - For more complex compliance testing: Consider using ansible-lint, Molecule, or OpenSCAP

- **Test Kitchen**: Replace with Molecule for Ansible role testing
  - Molecule provides similar functionality but is designed specifically for Ansible

- **Chef Automate/Infra Server**: Replace with Ansible Tower/AWX or other Ansible-native solutions
  - Consider using GitLab CI/CD or Jenkins for pipeline automation
  - Use Ansible Vault for secrets management

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 remains enabled and older protocols remain disabled
  - Consider updating to also include TLSv1.3 support

- **SSH Security**: Maintain the SSH root login restrictions from the InSpec test
  - Convert the InSpec control to an Ansible task that enforces the same policy

- **Credentials Management**: 
  - The Chef deployment scripts contain hardcoded credentials that should be moved to Ansible Vault
  - Identified credentials: 1 user password in each deployment script

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing solutions
  - Mitigation: Use Ansible's assert module for basic tests and consider Molecule for more complex testing scenarios

- **Compliance Reporting**: Chef InSpec provides compliance reporting that needs an equivalent in Ansible
  - Mitigation: Consider integrating with OpenSCAP or using Ansible Tower/AWX for compliance reporting

### Migration Order

1. **website_https.yml and poodle_fix.yml**: Already in Ansible format, no migration needed
2. **InSpec Tests**: Convert to Ansible-native testing solutions
   - website_https_verify.rb → Ansible assert tasks or Molecule tests
   - ssh_profile.rb → Ansible assert tasks or Molecule tests
3. **Chef Deployment Scripts**: Convert to Ansible playbooks
   - deploy-automate.sh → Ansible playbook for Chef Automate deployment
   - deploy-chef-server.sh → Ansible playbook for Chef Infra Server deployment

### Assumptions

1. The primary goal is to move away from Chef InSpec and use Ansible-native testing solutions
2. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) are working correctly and don't need modification
3. The deployment scripts for Chef Automate and Chef Infra Server are still needed but should be converted to Ansible
4. The target environment will continue to be Ubuntu 20.04 running on Vagrant
5. There are no external dependencies or integrations not visible in the provided files
6. The hardcoded credentials in the deployment scripts are for demonstration purposes only and will be replaced with Ansible Vault
7. The repository is primarily used for demonstration and educational purposes rather than production deployments