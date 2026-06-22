# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks designed to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

Estimated timeline: 1-2 weeks for a single developer, considering the limited scope and straightforward nature of the components.

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
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash script
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash script
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests - will need to be replaced with Ansible-native testing framework configuration
- `index.html`: Simple HTML file used for testing - can be preserved as-is or incorporated into Ansible content

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use the `ansible.builtin.assert` module for basic assertions
  - Option 2: Implement Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure the SSLProtocol settings are correctly migrated
  - Maintain the same level of TLS security (TLSv1.2)

- **SSH Security**: The SSH root login compliance check must be preserved
  - Convert the InSpec control to an equivalent Ansible check
  - Maintain the STIG compliance references and documentation

- **Vault/secrets management**:
  - Hardcoded credentials in deploy-automate.sh and deploy-chef-server.sh scripts (username, password)
  - These should be migrated to Ansible Vault or another secure secret management solution

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach
  - Mitigation: Use Ansible's assert module with well-structured test conditions
  - Consider implementing custom Ansible modules if complex assertions are needed

- **Compliance Metadata**: Preserving compliance metadata (STIG IDs, CCI references) from InSpec tests
  - Mitigation: Use Ansible task documentation fields to maintain this metadata
  - Consider implementing a custom Ansible callback plugin to generate compliance reports

- **Chef Automate Deployment**: Converting the Chef Automate deployment scripts to Ansible
  - Mitigation: Research Ansible modules for Chef management or create custom modules if needed
  - Consider using the `ansible.builtin.uri` module to interact with Chef APIs

### Migration Order

1. **website_https.yml and poodle_fix.yml**: Already in Ansible format, no migration needed
2. **InSpec Tests**: Convert to Ansible assertions or Molecule tests
   - website_https_verify.rb
   - ssh_profile.rb
3. **Deployment Scripts**: Convert to Ansible playbooks
   - deploy-automate.sh
   - deploy-chef-server.sh
4. **Test Infrastructure**: Replace kitchen.yml with Molecule configuration

### Assumptions

1. The primary goal is to eliminate Chef InSpec dependency while maintaining the same level of compliance testing
2. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are working correctly and don't need functional changes
3. The deployment scripts are used for setting up test environments and not production systems
4. The hardcoded credentials in the deployment scripts are for demonstration purposes only
5. The target environment will continue to be Ubuntu 20.04 or compatible systems
6. The migration doesn't need to address scaling or high-availability concerns
7. There are no external dependencies or integrations beyond what's visible in the repository
8. The InSpec tests are comprehensive and don't have hidden dependencies on other InSpec profiles