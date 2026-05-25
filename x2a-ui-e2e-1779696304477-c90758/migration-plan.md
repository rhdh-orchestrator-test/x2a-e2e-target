# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together for compliance automation. The primary focus is on using Chef InSpec for compliance testing alongside Ansible for configuration management. The migration will involve consolidating these technologies into a pure Ansible solution, leveraging Ansible's native testing capabilities or integrating with other testing frameworks.

The migration complexity is relatively low as the repository primarily contains Ansible playbooks already, with Chef InSpec being used only for testing. The estimated timeline for migration is 1-2 weeks, focusing on replacing InSpec tests with equivalent Ansible testing solutions.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL vulnerabilities in Apache by disabling older protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL configuration hardening, service restart handlers

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

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef server installation, user and organization creation

- **automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Sample HTML file for the web server. No migration considerations needed.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be infrastructure-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use the ansible-test framework for compliance testing

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: The deployment scripts need to be replaced with Ansible playbooks that can:
  - Set up equivalent compliance monitoring solution
  - Configure system settings (hostname, sysctl parameters)
  - Install and configure required packages

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Approach: Preserve the same SSL protocol restrictions in the Ansible roles
  
- **SSH Security**: The SSH root login compliance check needs to be maintained
  - Approach: Convert the InSpec control to an Ansible task that checks the same configuration

- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password)
  - Self-signed certificates generated in the playbooks
  - Migration should use Ansible Vault to secure these credentials

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible testing mechanisms
  - Mitigation: Use Ansible's assert module combined with uri module to test HTTP responses
  - For SSL testing, use the openssl_certificate_info module to validate configurations

- **Compliance Reporting**: InSpec provides structured compliance reporting that needs to be replicated
  - Mitigation: Consider integrating with tools like Ansible AWX/Tower for compliance reporting or use community modules for generating compliance reports

### Migration Order

1. **website_https.yml** (low risk, already Ansible): Review and optimize the existing Ansible playbook
2. **poodle_fix.yml** (low risk, already Ansible): Review and optimize the existing Ansible playbook
3. **InSpec Tests** (moderate complexity): Convert to Ansible-native testing
   - website_https_verify.rb
   - ssh_profile.rb
4. **Deployment Scripts** (high complexity): Convert bash scripts to Ansible playbooks
   - deploy-chef-server.sh
   - deploy-automate.sh

### Assumptions

1. The primary purpose of this repository is for demonstration of Chef InSpec with Ansible rather than production use
2. The hardcoded credentials in the deployment scripts are for demonstration purposes only
3. The target environment is Ubuntu 20.04 running on Vagrant VMs
4. There are no external dependencies or integrations beyond what's visible in the repository
5. The Chef InSpec tests are used only for validation and not for any runtime functionality
6. The deployment scripts are used for setting up a test environment and not for production deployment