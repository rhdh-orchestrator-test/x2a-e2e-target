# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Ansible playbooks and Chef InSpec tests that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on converting the existing Chef InSpec tests to Ansible's native testing capabilities while preserving the existing Ansible playbooks. The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited scope and clear separation of concerns between the configuration management (Ansible) and compliance testing (Chef InSpec) components.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2 in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security configuration
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible Molecule for testing.
- `index.html`: Simple HTML file used as a test page. No migration considerations needed.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible's native testing capabilities:
  - For basic tests: Use Ansible assert module and check_mode
  - For compliance testing: Migrate to ansible-lint or OpenSCAP with ansible-collection-compliance
  - Alternative: Keep InSpec tests but run them using the ansible.builtin.command module

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced and SSLv3 is disabled
  - Maintain the same level of security in the Apache configuration

- **SSH Security**: The SSH root login compliance check must be preserved
  - Migrate the InSpec control to an equivalent Ansible check
  - Maintain the STIG compliance references and documentation

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach
  - Mitigation: Use Ansible's assert module combined with command/shell modules to achieve similar functionality
  - Consider using the community.general.assert_that module for more expressive assertions

- **Compliance Reporting**: InSpec provides rich compliance reporting that needs to be replicated
  - Mitigation: Implement custom reporting using Ansible callbacks or integrate with tools like AWX/Tower for reporting

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format, only need review and potential refactoring
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity, convert to Ansible assertions or molecule tests
3. **Chef Automate Deployment Scripts**: Higher complexity, convert bash scripts to Ansible roles for infrastructure setup

### Assumptions

1. The primary goal is to eliminate Chef InSpec dependency while maintaining the same level of compliance testing
2. The existing Ansible playbooks are functioning correctly and don't require significant changes
3. The target environment will continue to be Ubuntu 20.04 or compatible systems
4. Test Kitchen is only used for development/testing and not in production pipelines
5. The Chef Automate and Chef Server deployment scripts are used for setting up test environments and not production infrastructure
6. No external data sources or dynamic inventory is being used with the current setup
7. The migration doesn't need to address scaling concerns as the examples appear to be for demonstration purposes
8. The self-signed certificates are acceptable for the target environment (not requiring integration with a certificate authority)