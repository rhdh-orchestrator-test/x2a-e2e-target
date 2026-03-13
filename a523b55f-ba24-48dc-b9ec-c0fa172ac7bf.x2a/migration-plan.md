# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible's native testing capabilities while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server deployment scripts that will need to be replaced with Ansible equivalents.

Estimated timeline: 1-2 weeks for a single developer, with minimal complexity due to the limited scope of Chef components.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration and self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website-https-verify**:
    - Description: Chef InSpec test that validates HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL/TLS protocol verification

- **ssh-profile**:
    - Description: Chef InSpec test that validates SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance checks with STIG references

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash with Chef CLI
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash with Chef CLI
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Sample HTML content for the web server

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible's native testing capabilities:
  - For basic tests: Use Ansible assert module
  - For more complex compliance testing: Integrate with Ansible Lint or Molecule
  - For comprehensive compliance: Consider migrating to ansible-compliance or integrating with OpenSCAP

- **Test Kitchen**: Replace with Molecule for Ansible role testing
  - Molecule provides similar functionality for testing Ansible roles with various drivers and verifiers

- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or AWX
  - For organization and user management, use Ansible Tower/AWX teams and organizations
  - For reporting and compliance, use Ansible Automation Platform's built-in capabilities

### Security Considerations

- **SSL/TLS Configuration**: Preserve the security hardening in the poodle_fix.yml playbook
  - Ensure the TLS protocol restrictions are maintained in the migrated solution
  - Consider updating to include newer TLS versions (TLS 1.3) while still disabling older protocols

- **SSH Hardening**: Maintain the SSH security controls from ssh_profile.rb
  - Convert the InSpec controls to Ansible assertions or include in hardening roles
  - Preserve the STIG compliance references for documentation and audit purposes

- **Self-signed Certificates**: Consider enhancing with Let's Encrypt integration
  - The current solution uses self-signed certificates which should be replaced with trusted certificates in production

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach
  - Solution: Use Ansible's assert module for basic tests and consider ansible-test or Molecule for more complex validations
  - For compliance testing, evaluate ansible-compliance or OpenSCAP integration

- **Chef Server Replacement**: Replacing Chef Server functionality with Ansible equivalent
  - Solution: Implement Ansible Automation Platform or AWX for centralized management
  - Develop Ansible playbooks to handle user/organization management similar to the Chef scripts

### Migration Order

1. Convert InSpec tests to Ansible tests (low risk, foundational)
   - website_https_verify.rb → Ansible assertions or Molecule tests
   - ssh_profile.rb → Ansible assertions or compliance role

2. Update Test Kitchen configuration to Molecule (moderate complexity)
   - kitchen.yml → molecule/default/molecule.yml

3. Create Ansible Automation Platform deployment playbook (high complexity)
   - Replace deploy-automate.sh and deploy-chef-server.sh with Ansible playbooks

### Assumptions

1. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) can be used as-is without modification
2. The repository is primarily used for demonstration/educational purposes rather than production deployment
3. The Chef InSpec tests are used only for validation and not for ongoing compliance monitoring
4. There are no additional Chef cookbooks or resources not visible in the repository structure
5. The migration target is Ansible without any Chef components
6. The deployment scripts for Chef Automate and Chef Server need to be replaced with equivalent Ansible Automation Platform deployment