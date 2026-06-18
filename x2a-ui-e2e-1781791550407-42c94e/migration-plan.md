# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks designed to demonstrate compliance automation with Ansible. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native solutions while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server deployment scripts that need to be migrated to Ansible playbooks.

The estimated timeline for this migration is 1-2 weeks, with low to moderate complexity. The primary challenge will be replacing Chef InSpec tests with equivalent Ansible testing frameworks while maintaining the same level of compliance validation.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

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
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Simple HTML file used for testing the web server. No migration needed, can be used as-is.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic validation
  - Option 2: Implement Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis and best practices validation

- **Test Kitchen**: Replace with Molecule for Ansible playbook testing

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that achieve the same configuration

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced and older protocols are disabled
  - Maintain proper certificate generation and configuration

- **SSH Hardening**: The SSH compliance checks must be preserved
  - Convert the InSpec SSH root login check to Ansible assertions or Molecule tests
  - Ensure compliance with security standards (SRG-OS-000112, V-38607)

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets detected in deployment scripts

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing style to Ansible's procedural approach
  - Mitigation: Use Ansible's assert module with carefully crafted conditions that match InSpec's intent
  - Consider implementing custom Ansible modules if needed for complex validations

- **Compliance Validation**: Ensuring the same level of compliance validation without InSpec
  - Mitigation: Document each compliance check and create equivalent Ansible tests
  - Consider using OpenSCAP with Ansible for more comprehensive compliance testing

- **Chef Server Deployment**: Replacing Chef server deployment with equivalent infrastructure
  - Mitigation: Evaluate if Chef server is still needed or if Ansible can fully replace its functionality
  - If Chef server is still required, create Ansible playbooks that perform the same installation and configuration

### Migration Order

1. **website_https.yml** (low risk, already Ansible): Review and optimize existing playbook
2. **poodle_fix.yml** (low risk, already Ansible): Review and optimize existing playbook
3. **website_https_verify.rb** (moderate complexity): Convert InSpec tests to Ansible assertions or Molecule tests
4. **ssh_profile.rb** (moderate complexity): Convert InSpec compliance checks to Ansible assertions or Molecule tests
5. **chef-server-deployment scripts** (high complexity): Create Ansible playbooks to replace Chef server deployment

### Assumptions

1. The primary goal is to eliminate Chef InSpec dependency while maintaining the same level of compliance validation
2. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are functioning correctly and only need minor adjustments
3. The deployment of Chef Automate/Infra Server is still required (if not, these components can be eliminated)
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. Vagrant will continue to be used for development/testing environments
6. No additional Chef cookbooks or resources are being used beyond what's visible in the repository
7. The hardcoded credentials in the deployment scripts are for testing purposes only and will be properly secured in production