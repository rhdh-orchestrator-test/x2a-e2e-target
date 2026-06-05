# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mixed environment of Chef InSpec tests and Ansible playbooks that are used together for compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single engineer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate the POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies the HTTPS website is properly configured
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that checks SSH configuration for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Sample HTML file used for testing the web server. Can be preserved as-is or included as a template in Ansible.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use the ansible-lint tool for static analysis
  - Option 4: Consider integrating with pytest-ansible for Python-based testing

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Replace with Ansible AWX/Tower or other Ansible-native management solutions

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced and older protocols are disabled
  - Maintain proper certificate generation and configuration

- **SSH Security**: The SSH compliance checks in ssh_profile.rb need to be converted to Ansible
  - Implement equivalent checks for PermitRootLogin settings
  - Preserve compliance with security standards (SRG-OS-000112, V-38607)

- **Vault/secrets management**:
  - Hardcoded credentials in deploy-automate.sh and deploy-chef-server.sh scripts (username, password)
  - Consider using Ansible Vault for securing these credentials

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions or Molecule tests
  - Challenge: InSpec has specific testing constructs that may not have direct equivalents in Ansible
  - Mitigation: Use a combination of Ansible assert module and custom modules where needed

- **Compliance Reporting**: InSpec provides compliance reporting capabilities
  - Challenge: Replicating compliance reporting functionality in Ansible
  - Mitigation: Consider integrating with tools like Ansible AWX/Tower for reporting or use community modules

- **Chef Server Deployment**: Converting Chef server deployment scripts to Ansible
  - Challenge: Ensuring idempotent installation and configuration
  - Mitigation: Use Ansible's package and service modules with appropriate state checks

### Migration Order

1. **website_https.yml and poodle_fix.yml** (already in Ansible, no migration needed)
2. **website_https_verify.rb** (convert InSpec tests to Ansible assertions or Molecule tests)
3. **ssh_profile.rb** (convert InSpec compliance checks to Ansible)
4. **deploy-chef-server.sh and deploy-automate.sh** (convert to Ansible playbooks)
5. **kitchen.yml** (replace with Molecule configuration)

### Assumptions

1. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) are working correctly and don't need modification beyond potential refactoring for best practices.
2. The primary goal is to eliminate Chef InSpec dependency while maintaining equivalent testing capabilities.
3. The deployment scripts for Chef Automate and Chef Infra Server will be replaced with Ansible playbooks that deploy alternative solutions or configure the same tools.
4. The target environment will continue to be Ubuntu 20.04 or compatible systems.
5. The security compliance requirements represented in the InSpec tests must be maintained in the Ansible solution.
6. No external data sources or integrations beyond what's visible in the repository are required.