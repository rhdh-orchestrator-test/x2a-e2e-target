# MIGRATION FROM CHEF/INSPEC TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on:

1. Chef InSpec test files that need to be migrated to Ansible-compatible testing frameworks
2. Chef Automate and Chef Server deployment scripts that need to be converted to Ansible playbooks
3. Existing Ansible playbooks that need to be reviewed and potentially refactored

The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited number of files and straightforward functionality.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
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
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Sample HTML file used for testing web server configuration

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Migrate to Ansible Molecule for integration testing
  - Use ansible-lint for static code analysis
  - Consider ansible-test for unit testing
  - For compliance testing similar to InSpec, evaluate:
    - OpenSCAP with ansible-playbook
    - Ansible Compliance as Code framework
    - Ansible Automation Platform's compliance capabilities

- **Test Kitchen**: Replace with:
  - Ansible Molecule for testing infrastructure
  - Molecule's Vagrant driver for local testing

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Ensure the SSLProtocol settings are preserved in the migrated Ansible roles
  - Consider expanding the TLS hardening to include modern best practices

- **SSH Security**: The SSH root login compliance check needs to be maintained
  - Migrate the InSpec control to an equivalent Ansible check
  - Consider implementing the actual SSH hardening as an Ansible task

- **Credentials Management**: 
  - The Chef deployment scripts contain hardcoded credentials that should be moved to Ansible Vault
  - Count: 3 credential sets in deploy-automate.sh and deploy-chef-server.sh (username, password, email)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible testing frameworks
  - Mitigation: Use Ansible assert modules or custom modules to implement similar validation logic
  - Consider using community.general.assert module for complex assertions

- **Chef Server Deployment**: Converting Chef Server deployment scripts to Ansible
  - Mitigation: Research existing Ansible roles for Chef Server deployment or create custom roles
  - Consider containerized deployment of Chef Server using Ansible container modules

### Migration Order

1. **Existing Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format
   - Review and refactor according to Ansible best practices
   - Convert to role-based structure for better reusability

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity
   - Convert to Ansible Molecule tests or equivalent testing framework
   - Ensure all compliance checks are preserved

3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity
   - Convert to Ansible playbooks with proper variable management
   - Implement Ansible Vault for credential storage

### Assumptions

1. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are functional and don't require significant changes beyond refactoring to follow best practices.

2. The InSpec tests are used primarily for validation and compliance checking, not for actual configuration management.

3. The Chef Automate and Chef Server deployment scripts are used for setting up testing environments and not for production deployments.

4. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.

5. There are no external dependencies or integrations not visible in the provided files.

6. The migration will maintain the same level of security compliance as the original implementation.

7. No custom Chef resources or complex Chef-specific functionality is present that would require special handling during migration.