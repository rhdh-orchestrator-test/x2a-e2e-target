# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on converting the Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
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
    - Key Features: SSH configuration validation with security tags (STIG, CCI)

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests in a Vagrant environment
- `index.html`: Sample HTML file for the web server

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - **Option 1**: Use Ansible's `assert` module for basic testing
  - **Option 2**: Integrate with Molecule for more comprehensive testing
  - **Option 3**: Use ansible-lint for static analysis
  - **Option 4**: For compliance testing similar to InSpec, consider integrating OpenSCAP with Ansible

- **Test Kitchen**: Replace with:
  - **Option 1**: Molecule for Ansible role testing
  - **Option 2**: Ansible's own testing framework

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure the SSLProtocol settings are correctly migrated
  - Maintain the same level of security by disabling SSLv3 and only enabling TLSv1.2

- **SSH Security**: The SSH root login check must be preserved
  - Convert the InSpec control to an Ansible task that checks the same configuration
  - Maintain the security tags and documentation for compliance reporting

- **Vault/secrets management**:
  - Hardcoded credentials in the Chef Automate deployment scripts (username, password)
  - Consider using Ansible Vault to secure these credentials

### Technical Challenges

- **Challenge 1**: Converting InSpec tests to Ansible assertions
  - Mitigation: Create custom Ansible modules or use the assert module with appropriate conditions
  - For complex tests, consider using Molecule with testinfra as a Python-based alternative

- **Challenge 2**: Preserving compliance metadata
  - Mitigation: Document compliance information in Ansible task comments or in separate documentation
  - Consider using Ansible tags to mark tasks with compliance identifiers

- **Challenge 3**: Chef Automate deployment conversion
  - Mitigation: Research Ansible roles for deploying Chef products or create custom roles
  - Consider whether Chef Automate is still needed or if it can be replaced with Ansible Tower/AWX

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format
   - Review and update as needed for best practices
   - Ensure idempotency and proper error handling

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity
   - Convert to Ansible assertions or Molecule tests
   - Ensure all security checks are preserved

3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity
   - Convert to Ansible playbooks
   - Secure credentials with Ansible Vault
   - Consider if Chef components are still needed or can be replaced with Ansible alternatives

### Assumptions

1. The existing Ansible playbooks are functioning correctly and don't require significant changes
2. The target environment will continue to be Ubuntu 20.04 or compatible
3. The compliance requirements represented in the InSpec tests are still valid and necessary
4. The deployment of Chef Automate and Chef Infra Server is still required (rather than being replaced entirely by Ansible)
5. No external dependencies or integrations beyond what's visible in the repository
6. The migration will maintain the same level of security and compliance checking
7. No custom InSpec resources are being used that would require special handling