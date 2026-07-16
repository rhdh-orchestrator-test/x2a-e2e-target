# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Ansible playbooks and Chef InSpec tests that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on converting the InSpec tests to Ansible-compatible testing frameworks while maintaining the existing Ansible playbooks. Additionally, there are Chef server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium
**Primary Focus**: Converting InSpec tests to Ansible-native testing solutions

## Module Migration Plan

This repository contains Ansible playbooks, Chef InSpec tests, and Chef server deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling older protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and port availability
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port checking, HTTPS verification, SSL protocol validation

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance checking

- **chef-automate-deployment**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-compatible testing framework configuration.
- `index.html`: Sample HTML file used for testing the web server deployment.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - **Option 1**: Ansible Molecule with Testinfra for infrastructure testing
  - **Option 2**: Ansible Molecule with Goss for lightweight testing
  - **Option 3**: Maintain InSpec as a standalone tool but integrate with Ansible workflows

- **Test Kitchen**: Replace with Ansible Molecule for test orchestration

- **Chef Server/Automate**: Replace deployment scripts with Ansible playbooks that can:
  - Configure system requirements
  - Deploy alternative configuration management or compliance tools as needed

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Ensure TLS 1.2 remains enforced
  - Maintain proper certificate generation and management

- **SSH Security**: The SSH root login compliance check must be preserved in the new testing framework
  - Convert the InSpec control to equivalent tests in the chosen testing framework
  - Maintain the security metadata (tags, impact levels) for compliance reporting

- **Vault/secrets management**:
  - Hardcoded credentials in the Chef deployment scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deployment scripts

### Technical Challenges

- **Testing Framework Conversion**: Converting InSpec tests to another testing framework requires careful mapping of test assertions
  - Mitigation: Create a mapping document for InSpec resources to Testinfra/Goss equivalents
  - Ensure all compliance metadata is preserved in the new format

- **Maintaining Compliance Reporting**: InSpec provides rich compliance reporting that must be preserved
  - Mitigation: Evaluate if the chosen testing framework can generate similar compliance reports
  - Consider maintaining InSpec as a standalone tool if reporting capabilities are critical

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format
   - Review and update as needed for best practices
   - No actual migration needed, just potential optimization

2. **Testing Framework** (InSpec tests): Medium complexity
   - Set up the chosen testing framework (Molecule with Testinfra/Goss)
   - Convert InSpec tests to the new framework
   - Validate that all tests provide the same coverage

3. **Chef Deployment Scripts**: Higher complexity
   - Create Ansible playbooks to replace the Chef server deployment scripts
   - Test thoroughly to ensure equivalent functionality

### Assumptions

1. The primary goal is to consolidate on Ansible as the configuration management tool while maintaining equivalent testing capabilities.
2. The InSpec tests are used primarily for validation and compliance checking, not for active remediation.
3. There is no requirement to maintain backward compatibility with Chef InSpec after migration.
4. The deployment scripts for Chef Automate/Server will be replaced with equivalent functionality using alternative tools or simply Ansible playbooks for environment setup.
5. The current setup appears to be a demonstration/example environment rather than a production system, which may simplify migration requirements.
6. No external data sources or integrations are referenced that would need to be preserved in the migration.
7. The security compliance requirements (particularly around SSH and SSL) must be maintained in any new testing framework.