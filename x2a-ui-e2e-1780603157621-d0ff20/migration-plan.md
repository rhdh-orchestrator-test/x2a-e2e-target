# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, including testing and documentation.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling older protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Simple HTML file used for testing the web server. No migration needed as it's a static file.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing
  - Option 4: Keep InSpec but invoke it from Ansible using the `command` module

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - GitLab CI/Jenkins for pipeline integration
  - Compliance scanning tools like OpenSCAP or Ansible's built-in security roles

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook that disables vulnerable SSL protocols.
  - Migration approach: Preserve the same configuration in the Ansible playbooks.

- **SSH Security**: The SSH root login check in ssh_profile.rb needs to be maintained.
  - Migration approach: Convert to Ansible assert or use ansible-lint security rules.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault.
  - Self-signed certificates are generated in the playbook; consider using ansible-vault for storing private keys.
  - Count of credentials detected:
    - website_https.yml: 0 hardcoded credentials
    - deploy-automate.sh: 1 hardcoded password
    - deploy-chef-server.sh: 1 hardcoded password

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's domain-specific language to Ansible assertions or another testing framework will require careful mapping of test logic.
  - Mitigation: Create a mapping document for common InSpec resources to Ansible assertions.

- **Compliance Reporting**: InSpec provides rich compliance reporting that needs to be replicated.
  - Mitigation: Integrate with tools like OpenSCAP or use Ansible's json_query to format test results.

- **Chef Server Functionality**: Replacing Chef Server's organization and user management.
  - Mitigation: Use Ansible AWX/Tower for role-based access control and inventory management.

### Migration Order

1. **website_https.yml and poodle_fix.yml**: Already in Ansible format, no migration needed (low risk, high value)
2. **InSpec Tests**: Convert to Ansible-compatible testing (moderate complexity)
   - website_https_verify.rb
   - ssh_profile.rb
3. **Chef Deployment Scripts**: Convert to Ansible playbooks (high complexity)
   - deploy-automate.sh
   - deploy-chef-server.sh

### Assumptions

1. The primary goal is to move away from Chef InSpec while maintaining the existing Ansible playbooks.
2. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs.
3. The security compliance requirements (STIG references in ssh_profile.rb) must be maintained in the new solution.
4. The repository is primarily for demonstration/educational purposes rather than production use, based on the README description.
5. The hardcoded credentials in the deployment scripts are not used in production environments.
6. The self-signed certificates are acceptable for the demonstration environment.
7. The Chef Automate and Chef Server deployment needs to be replaced with equivalent Ansible Tower/AWX setup.