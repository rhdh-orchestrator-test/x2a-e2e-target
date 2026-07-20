# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations that need to be consolidated into a unified Ansible solution. The repository primarily consists of:

1. Chef Automate and Chef Infra Server deployment scripts
2. Ansible playbooks for configuring HTTPS websites with Apache
3. Chef InSpec tests for compliance verification

The migration complexity is relatively low as most of the configuration is already in Ansible format. The primary focus will be on replacing the Chef Automate/Infra Server deployment scripts with Ansible equivalents and ensuring the InSpec tests can be integrated into an Ansible-based workflow. Estimated timeline: 1-2 weeks for a complete migration.

## Module Migration Plan

This repository contains Chef and Ansible configurations that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for configuring HTTPS websites with Apache and InSpec tests for compliance verification
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL hardening, InSpec compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook that configures an Apache web server with HTTPS support. Migration considerations include ensuring SSL certificate generation is handled properly in the target environment.
  
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook that hardens SSL configuration to prevent POODLE attacks. Migration considerations include ensuring compatibility with the target environment's Apache version.
  
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec. Migration considerations include replacing with Ansible-native testing frameworks or adapting to work with Ansible.
  
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality. Migration considerations include converting to Ansible test format or maintaining InSpec integration.
  
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance. Migration considerations include converting to Ansible test format or maintaining InSpec integration.
  
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Migration considerations include replacing with Ansible roles for infrastructure management.
  
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Migration considerations include replacing with Ansible roles for infrastructure management.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml configuration)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions like Molecule or maintain InSpec integration through the ansible_inspec module
- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible roles for infrastructure management or eliminate if moving entirely to Ansible-based workflow
- **Test Kitchen**: Replace with Molecule for Ansible role testing

### Security Considerations

- **SSL Configuration**: The migration must maintain the SSL hardening present in the poodle_fix.yml playbook
- **SSH Hardening**: The SSH security profile in ssh_profile.rb must be maintained in the Ansible configuration
- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be moved to Ansible Vault
  - SSL certificates in the website_https.yml playbook should use Ansible Vault or a secrets management solution

### Technical Challenges

- **InSpec Test Integration**: Determining whether to convert InSpec tests to Ansible-native testing or maintain InSpec integration
- **Chef Server Replacement**: If Chef Server functionality is required, determining how to replace it with Ansible-equivalent solutions
- **Compliance Automation**: Ensuring the compliance automation capabilities provided by InSpec are maintained in the Ansible workflow

### Migration Order

1. Ansible Playbooks (chef-and-ansible/website_https.yml, chef-and-ansible/poodle_fix.yml) - low risk, already in Ansible format
2. Testing Framework (chef-and-ansible/kitchen.yml, InSpec tests) - moderate complexity, requires decision on testing approach
3. Chef Deployment Scripts (setup-automate/*) - high complexity, requires replacement with Ansible roles or elimination

### Assumptions

1. The primary goal is to consolidate all configuration management into Ansible, eliminating Chef dependencies
2. InSpec testing is a requirement and needs to be maintained or replaced with equivalent functionality
3. The Chef Automate and Chef Infra Server deployment is part of the infrastructure that needs to be managed by Ansible
4. The target environment will continue to be Ubuntu 20.04 or compatible
5. The hardcoded credentials in the setup scripts are for testing purposes and will be replaced with secure alternatives
6. The SSL configuration requirements (TLS 1.2, disabled SSLv3) must be maintained in the migrated solution