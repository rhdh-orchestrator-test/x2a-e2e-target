# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. The repository also contains shell scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible components are already in place. The main migration effort will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Migrating Chef Automate/Infra Server deployment scripts to Ansible playbooks
3. Ensuring all compliance checks are preserved in the new implementation

Estimated timeline: 1-2 weeks for a small team (1-2 engineers)

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
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file for testing web server functionality

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic compliance checks
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Ansible's built-in `--check` mode for validation

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX or Tower for enterprise automation platform
  - GitLab CI/CD or Jenkins for pipeline automation
  - Compliance automation can be handled by OpenSCAP integration with Ansible

### Security Considerations

- **SSL Configuration**: The current implementation fixes POODLE vulnerability by enforcing TLSv1.2. Migration should maintain or enhance this security posture.
  - Migration approach: Preserve the SSL hardening in Ansible roles, consider updating to include TLSv1.3 support

- **SSH Hardening**: The InSpec test verifies SSH root login is disabled.
  - Migration approach: Create an Ansible role for SSH hardening that implements the same controls

- **Self-signed Certificates**: The current implementation uses self-signed certificates.
  - Migration approach: Maintain the same approach but consider adding support for Let's Encrypt as an option

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach.
  - Mitigation: Use Ansible's assert module with carefully crafted conditions that match InSpec's intent

- **Compliance Reporting**: InSpec provides rich compliance reporting that may be difficult to replicate in Ansible.
  - Mitigation: Consider integrating with OpenSCAP or maintaining a hybrid approach where Ansible runs InSpec

- **Chef Server Deployment**: The current scripts deploy Chef Server with specific configurations.
  - Mitigation: Create equivalent Ansible roles for AWX/Tower deployment with similar user/org management

### Migration Order

1. **website_https playbook** (low risk, already in Ansible)
   - Only needs review and potential refactoring to follow best practices

2. **poodle_fix playbook** (low risk, already in Ansible)
   - Only needs review and potential refactoring to follow best practices

3. **InSpec tests** (moderate complexity)
   - Convert to Ansible assertions or Molecule tests
   - Ensure all compliance checks are preserved

4. **Chef deployment scripts** (high complexity)
   - Convert to Ansible roles for AWX/Tower deployment
   - Implement secure credential management with Ansible Vault

### Assumptions

1. The primary goal is to move all functionality to pure Ansible without dependency on Chef components
2. The current implementation is used for demonstration/testing rather than production
3. The security compliance requirements (e.g., STIG references in InSpec tests) must be maintained
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. The deployment scripts are examples and may need customization for actual environments
6. No external data sources or integrations beyond what's visible in the repository
7. The migration will preserve the self-service deployment capability of the original scripts
8. No specific performance requirements are assumed beyond maintaining current functionality