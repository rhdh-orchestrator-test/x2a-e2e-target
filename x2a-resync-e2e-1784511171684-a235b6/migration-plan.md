# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations that need to be migrated to a unified Ansible approach. The repository primarily consists of:

1. Ansible playbooks for configuring HTTPS websites with Apache
2. Chef InSpec tests for validating security compliance
3. Chef Automate and Chef Infra Server deployment scripts

The migration complexity is relatively low as most of the infrastructure code is already in Ansible format. The primary focus will be on converting the Chef InSpec tests to Ansible-compatible testing frameworks and replacing the Chef Automate/Infra Server deployment scripts with Ansible equivalents.

Estimated timeline: 2-3 weeks for a complete migration, with the majority of time spent on setting up equivalent compliance testing in Ansible.

## Module Migration Plan

This repository contains Chef and Ansible configurations that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Directory containing Ansible playbooks and Chef InSpec tests for configuring and validating HTTPS websites
    - Path: chef-and-ansible
    - Technology: Mixed (Ansible playbooks, Chef InSpec tests)
    - Key Features: Apache HTTPS configuration, SSL security hardening, compliance testing

- **setup-automate**:
    - Description: Directory containing Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server configuration, user and organization setup

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook for configuring Apache with HTTPS
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability in Apache
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification
- `chef-and-ansible/index.html`: Sample HTML file used in the website deployment example
- `chef-and-ansible/tests/website_https_verify.rb`: Chef InSpec test for validating HTTPS configuration
- `chef-and-ansible/tests/ssh_profile.rb`: Chef InSpec test for validating SSH security configuration
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server only
- `README.md`: Documentation file explaining the repository purpose

### Target Details

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Molecule for Ansible role testing
  - Option 2: Ansible's assert module for basic compliance checks
  - Option 3: Integration with other compliance tools like Ansible Lint or OpenSCAP

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Ansible's built-in testing capabilities

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - GitLab CI/CD or Jenkins for pipeline automation
  - Ansible Vault for secrets management

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening present in the poodle_fix.yml playbook
  - Approach: Preserve the SSL protocol restrictions in the Apache configuration
  
- **SSH Security**: Maintain the SSH root login restrictions verified by the InSpec tests
  - Approach: Create equivalent Ansible tasks to enforce SSH security configurations

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - SSL certificates are generated dynamically but should be managed securely in the new implementation

### Technical Challenges

- **Compliance Testing**: Converting Chef InSpec tests to Ansible-compatible testing frameworks
  - Mitigation: Use Ansible's assert module for basic compliance checks or integrate with tools like Molecule for more comprehensive testing

- **Infrastructure Deployment**: Replacing Chef Automate/Infra Server with Ansible-based alternatives
  - Mitigation: Document clear procedures for setting up Ansible AWX/Tower as a replacement for Chef Automate's functionality

### Migration Order

1. **Ansible Playbooks** (low risk, already in Ansible format)
   - No conversion needed, just organization into proper Ansible roles/structure
   - Files: chef-and-ansible/website_https.yml, chef-and-ansible/poodle_fix.yml

2. **Compliance Testing** (moderate complexity)
   - Convert InSpec tests to Ansible-compatible testing frameworks
   - Files: chef-and-ansible/tests/website_https_verify.rb, chef-and-ansible/tests/ssh_profile.rb

3. **Chef Infrastructure Deployment** (high complexity)
   - Replace Chef Automate/Infra Server deployment scripts with Ansible playbooks for setting up Ansible AWX/Tower
   - Files: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, not for production deployment.

2. The Chef components (InSpec tests and deployment scripts) are intended to be replaced with Ansible-native solutions rather than maintained as-is.

3. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the solution should be adaptable to other environments.

4. The security requirements (HTTPS configuration, SSL protocol restrictions, SSH hardening) must be maintained in the migrated solution.

5. The current implementation uses self-signed certificates for demonstration purposes, which may need to be replaced with proper certificate management in a production environment.

6. The hardcoded credentials in the Chef deployment scripts are for demonstration purposes and should be replaced with secure credential management in the migrated solution.