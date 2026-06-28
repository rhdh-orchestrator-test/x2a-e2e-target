# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus is on using Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook for deploying a secure Apache web server with SSL/TLS configuration
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook for fixing SSL vulnerabilities (POODLE) in Apache configuration
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test for verifying HTTPS website functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL/TLS protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control for verifying SSH security configuration (root login disabled)
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

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible Molecule for testing.
- `index.html`: Simple HTML file used for testing web server deployment. Migration consideration: Keep as-is or include as a template in Ansible.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible Molecule with Testinfra for infrastructure testing
  - Option 2: Use Ansible Molecule with Goss for compliance testing
  - Option 3: Keep InSpec but integrate with Ansible using the ansible_inspec module

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure code

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Tower/AWX for orchestration and job scheduling
  - Ansible Collections for configuration management
  - Compliance scanning tools like OpenSCAP or Ansible Compliance

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the Apache configuration, particularly the TLS protocol restrictions.
  - Approach: Use Ansible's `lineinfile` or `template` modules to manage the SSL configuration

- **SSH Security Controls**: The SSH security controls tested by InSpec need to be implemented and verified in Ansible.
  - Approach: Use Ansible's `lineinfile` or `template` modules to configure SSH, and Molecule with Testinfra to verify

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates and keys should be managed securely using Ansible Vault or external secret management
  - Count of credentials detected: 3 (username, password, and SSL keys)

### Technical Challenges

- **Testing Framework Transition**: Moving from Chef InSpec to an Ansible-compatible testing framework.
  - Mitigation: Create a mapping of InSpec resources to equivalent Testinfra or Goss tests
  - Example: InSpec's `describe port(443)` becomes Testinfra's `host.socket("tcp://0.0.0.0:443").is_listening`

- **Compliance Reporting**: Chef InSpec provides rich compliance reporting that needs to be replicated.
  - Mitigation: Implement Ansible Compliance or integrate with OpenSCAP for compliance reporting

- **Chef Automate Functionality**: Replacing Chef Automate's compliance dashboard and reporting.
  - Mitigation: Implement Ansible Tower/AWX with compliance reporting plugins or integrate with a dedicated compliance tool

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format, may need minor adjustments for best practices
2. **Testing Framework** (website_https_verify.rb, ssh_profile.rb): Moderate complexity, requires converting InSpec tests to Ansible-compatible testing
3. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity, requires replacing Chef Automate/Server with Ansible Tower/AWX

### Assumptions

1. The primary goal is to move all functionality to Ansible, eliminating the dependency on Chef components
2. The existing Ansible playbooks follow best practices and don't require significant refactoring
3. The target environment will continue to be Ubuntu 20.04 or compatible systems
4. Test Kitchen is only used for development/testing and not in production pipelines
5. There are no external dependencies or integrations not visible in the provided files
6. The hardcoded credentials in the deployment scripts are for demonstration purposes only
7. The compliance requirements represented by the InSpec tests are still valid and need to be maintained
8. The deployment scripts are used for setting up development/test environments, not production systems