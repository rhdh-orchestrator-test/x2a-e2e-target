# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate. The estimated timeline for migration would be 1-2 weeks, with low complexity as most components are already in Ansible format.

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
    - Key Features: SSH configuration validation, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server setup, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file used in the website deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but the deployment scripts suggest they could be used in cloud environments

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Convert InSpec tests to Ansible roles with test tasks

- **Test Kitchen**: Replace with Molecule for Ansible role testing
  - Molecule provides similar functionality but is designed specifically for Ansible

- **Chef Automate/Infra Server**: Replace with Ansible automation platform
  - AWX/Ansible Tower for web UI and job scheduling
  - Ansible Galaxy for role sharing
  - Ansible Vault for secrets management

### Security Considerations

- **SSL Configuration**: The poodle_fix.yml playbook addresses SSL security concerns
  - Migration approach: Maintain the same security hardening in Ansible roles
  - Consider updating to include more recent SSL/TLS best practices

- **SSH Security**: The ssh_profile.rb InSpec test verifies SSH security configuration
  - Migration approach: Convert to Ansible security role with appropriate checks
  - Implement as part of a broader security compliance role

- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password)
  - Migration approach: Move credentials to Ansible Vault

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing
  - Mitigation: Use Ansible assert module or custom modules for testing
  - Consider maintaining InSpec tests if they provide value not easily replicated in Ansible

- **Chef Server Functionality**: Replacing Chef Server functionality with Ansible equivalents
  - Mitigation: Map Chef Server features to Ansible Tower/AWX features
  - Document workflow changes for teams transitioning from Chef to Ansible

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk as they're already in Ansible format
   - Review and refactor into proper Ansible roles
   - Update to follow current Ansible best practices

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb) - Moderate complexity
   - Convert to Ansible-native testing or Molecule tests
   - Ensure all compliance checks are maintained

3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh) - High complexity
   - Replace with Ansible playbooks for deploying Ansible automation platform
   - Create migration documentation for users transitioning from Chef to Ansible

### Assumptions

1. The primary purpose of this repository is demonstration/educational rather than production use
2. The InSpec tests are used for compliance validation of infrastructure provisioned by Ansible
3. There are no additional Chef cookbooks or resources not visible in the repository structure
4. The deployment scripts are used for setting up Chef infrastructure, not application deployment
5. No external dependencies or integrations beyond what's visible in the code
6. No complex state management or data persistence requirements
7. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
8. Users will transition from Chef InSpec to Ansible-native testing solutions
9. No custom Chef resources or handlers are in use
10. The hardcoded credentials in deployment scripts are for demonstration purposes only