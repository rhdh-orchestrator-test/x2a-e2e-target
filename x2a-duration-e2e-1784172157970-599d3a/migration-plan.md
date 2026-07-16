# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks designed to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Server deployment scripts that need to be converted to Ansible playbooks.

Estimated timeline: 1-2 weeks for a single developer, considering the limited scope and complexity.

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
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled
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

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Simple HTML file used as a test page for the web server

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic validation
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use the ansible-lint tool for static analysis

- **Test Kitchen**: Replace with Molecule for Ansible role testing

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced and older protocols are disabled
  - Maintain proper certificate generation and management

- **SSH Security**: Preserve the SSH security controls from the InSpec test
  - Ensure root login remains disabled
  - Maintain compliance with referenced security standards (STIG)

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions or Molecule tests
  - Challenge: InSpec provides domain-specific language for compliance testing that doesn't directly map to Ansible
  - Mitigation: Use a combination of Ansible assert module and custom modules where needed

- **Chef Server Deployment**: Converting Chef server deployment scripts to Ansible
  - Challenge: The scripts install Chef-specific components that may not have direct Ansible equivalents
  - Mitigation: Research Ansible roles for Chef deployment or create custom roles

### Migration Order

1. **website_https.yml** (low risk, already Ansible)
   - No migration needed, but review for best practices and potential improvements

2. **poodle_fix.yml** (low risk, already Ansible)
   - No migration needed, but review for best practices and potential improvements

3. **website_https_verify.rb** (moderate complexity)
   - Convert InSpec tests to Ansible assertions or Molecule tests

4. **ssh_profile.rb** (moderate complexity)
   - Convert InSpec compliance controls to Ansible security role or Molecule tests

5. **deploy-automate.sh and deploy-chef-server.sh** (high complexity)
   - Convert bash scripts to Ansible playbooks
   - Implement proper secret management with Ansible Vault

### Assumptions

1. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) are working correctly and don't require functional changes
2. The InSpec tests are currently used for validation and compliance checking, and this functionality needs to be preserved
3. The deployment scripts for Chef Automate and Chef Server are still relevant and need to be converted to Ansible
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. The security requirements specified in the InSpec tests must be maintained in the Ansible implementation
6. No additional Chef cookbooks or resources are being used beyond what's visible in the repository
7. The migration doesn't need to preserve Test Kitchen functionality as it will be replaced with Ansible-native testing tools