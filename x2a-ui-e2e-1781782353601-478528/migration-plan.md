# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **inspec_tests**:
    - Description: Chef InSpec tests for verifying HTTPS functionality and SSH security compliance
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: Port listening checks, HTTPS verification, SSL protocol validation, SSH configuration validation

- **chef_automate_deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef_server_deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Simple HTML file used as a test page. No migration needed, can be used as-is.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic tests
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - GitLab CI/Jenkins for pipeline integration
  - Compliance scanning can be handled by OpenSCAP integrated with Ansible

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with TLS 1.2 and disable older protocols. This security practice should be maintained in the migrated solution.
  
- **SSH Hardening**: The InSpec tests verify SSH root login is disabled. This check should be preserved in the migrated testing framework.

- **Self-signed Certificates**: The playbook generates self-signed certificates. Consider enhancing security by integrating with Let's Encrypt in the migrated solution.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets detected in deployment scripts

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach may require additional logic and careful validation to ensure equivalent test coverage.
  - Mitigation: Create custom Ansible modules or use community modules that provide similar functionality to InSpec resources.

- **Chef Server Deployment**: Replacing Chef Server deployment with equivalent Ansible functionality requires understanding of Chef Server's components and finding Ansible alternatives.
  - Mitigation: Use AWX/Tower for web UI and job scheduling, GitLab/Jenkins for CI/CD, and OpenSCAP for compliance scanning.

### Migration Order

1. **website_https playbook** (low risk, already in Ansible)
   - Review and optimize existing Ansible playbook
   - No conversion needed, just potential improvements

2. **poodle_fix playbook** (low risk, already in Ansible)
   - Review and optimize existing Ansible playbook
   - No conversion needed, just potential improvements

3. **InSpec tests** (moderate complexity)
   - Convert to Ansible-compatible testing framework
   - Ensure equivalent test coverage and validation

4. **Chef deployment scripts** (high complexity)
   - Create Ansible playbooks to replace Chef Automate and Chef Server deployment
   - Implement secure credential management with Ansible Vault

### Assumptions

1. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) are working correctly and don't need functional changes, just potential optimization.

2. The InSpec tests are currently being used with Test Kitchen to validate the Ansible playbooks, and this testing workflow needs to be preserved.

3. The deployment scripts for Chef Automate and Chef Server are used for setting up infrastructure that will be replaced by Ansible AWX/Tower or other alternatives.

4. The hardcoded credentials in the deployment scripts are not used in production environments and will be properly secured in the migrated solution.

5. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.

6. The migration will maintain or improve the current security posture, particularly around SSL/TLS configuration and SSH hardening.