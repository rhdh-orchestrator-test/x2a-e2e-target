# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited number of components and clear separation of concerns.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Main directory containing Ansible playbooks and InSpec tests for HTTPS website deployment and validation
    - Path: chef-and-ansible
    - Technology: Ansible + Chef InSpec
    - Key Features: Apache configuration, SSL/TLS security, compliance testing

- **setup-automate**:
    - Description: Scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash + Chef
    - Key Features: Chef Server installation, Chef Automate installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible Molecule for testing.
- `chef-and-ansible/index.html`: Simple HTML file used as a test artifact. No migration needed, can be used as-is.
- `chef-and-ansible/website_https.yml`: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook that remediates SSL POODLE vulnerability in Apache by enforcing TLSv1.2.
- `chef-and-ansible/tests/website_https_verify.rb`: Chef InSpec test that verifies HTTPS functionality and security.
- `chef-and-ansible/tests/ssh_profile.rb`: Chef InSpec control that verifies SSH root login is disabled.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - For infrastructure testing: Replace with Ansible Molecule
  - For compliance testing: Consider using ansible-lint with custom rules or Ansible Molecule with testinfra

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure code

- **Chef Automate/Server**: The deployment scripts suggest these are used for compliance reporting and Chef management. Consider:
  - For compliance reporting: AWX/Ansible Tower with custom reporting
  - For configuration management: AWX/Ansible Tower

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable SSL3. This security hardening should be preserved in the Ansible migration.
  - Migration approach: Maintain the same SSL/TLS configurations in the Ansible tasks

- **SSH Security**: The InSpec test verifies SSH root login is disabled.
  - Migration approach: Create an equivalent Ansible role with both configuration and verification tasks

- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates are generated during deployment and should be handled securely

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing solutions will require careful mapping of test assertions.
  - Mitigation strategy: Use Ansible Molecule with testinfra for similar testing capabilities

- **Compliance Reporting**: If Chef Automate is being used for compliance reporting, finding an equivalent in the Ansible ecosystem.
  - Mitigation strategy: Consider AWX/Ansible Tower with custom reporting dashboards or integration with third-party compliance tools

### Migration Order

1. **Ansible Playbooks** (`chef-and-ansible/website_https.yml`, `chef-and-ansible/poodle_fix.yml`): Low risk as they can remain largely unchanged
2. **InSpec Tests** (`chef-and-ansible/tests/website_https_verify.rb`, `chef-and-ansible/tests/ssh_profile.rb`): Moderate complexity to convert to Ansible-native testing
3. **Chef Server/Automate Deployment Scripts** (`setup-automate/deploy-chef-server.sh`, `setup-automate/deploy-automate.sh`): Higher complexity, requires replacing with Ansible roles for equivalent functionality

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production, as indicated by the README.md mentioning these are "examples" related to a white paper.
2. The Chef InSpec tests are used for validation only and not for active remediation.
3. There are no external dependencies on Chef-specific features that would complicate migration.
4. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with secure alternatives in production.
5. The migration will maintain the same level of security validation currently provided by the InSpec tests.
6. The target environment will continue to be Ubuntu 20.04 as specified in the kitchen.yml file.