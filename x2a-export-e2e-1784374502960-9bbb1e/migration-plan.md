# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus is on using Chef InSpec for compliance testing alongside Ansible for configuration management. There are also Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity for the Ansible components (which are already in Ansible format) and moderate complexity for converting the InSpec tests to Ansible-compatible testing frameworks.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Main module containing Ansible playbooks and InSpec tests for HTTPS website deployment and compliance testing
    - Path: chef-and-ansible
    - Technology: Ansible + Chef InSpec
    - Key Features: Apache configuration, SSL certificate generation, compliance testing

- **setup-automate**:
    - Description: Module containing deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-specific testing framework like Molecule.
- `chef-and-ansible/index.html`: Simple HTML file used as a test page. Can be directly used in Ansible without modification.
- `chef-and-ansible/website_https.yml`: Ansible playbook that sets up an Apache web server with HTTPS using self-signed certificates.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability.
- `chef-and-ansible/tests/website_https_verify.rb`: Chef InSpec test that verifies HTTPS functionality and security.
- `chef-and-ansible/tests/ssh_profile.rb`: Chef InSpec test that verifies SSH security configuration.
- `setup-automate/deploy-automate.sh`: Bash script to deploy Chef Automate and Chef Infra Server.
- `setup-automate/deploy-chef-server.sh`: Bash script to deploy Chef Infra Server without Automate.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment (based on comments in setup scripts)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis
  - Option 4: Consider maintaining InSpec as a separate testing tool if deeply integrated

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Replace with:
  - AWX/Ansible Tower for web UI and job scheduling
  - Ansible Automation Platform for enterprise features
  - Git repositories for playbook/role storage

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with TLS 1.2 and disable older protocols. Migration should maintain or enhance this security posture.
  - Migration approach: Preserve the same SSL configuration in Ansible playbooks

- **SSH Security**: InSpec tests verify SSH root login is disabled.
  - Migration approach: Create equivalent Ansible assertions or use ansible-lint rules

- **Self-signed Certificates**: The playbooks generate self-signed certificates.
  - Migration approach: Use Ansible's `openssl_*` modules (already in use) or consider integrating with Let's Encrypt for production environments

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require careful mapping of test assertions.
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules/assertions

- **Compliance Reporting**: If compliance reporting is a key feature, ensure the Ansible solution provides equivalent capabilities.
  - Mitigation: Evaluate Ansible Automation Platform's compliance capabilities or integrate with third-party compliance tools

- **Chef Automate Features**: If specific Chef Automate features are being used, ensure equivalent functionality in Ansible ecosystem.
  - Mitigation: Map Chef Automate features to Ansible Tower/AWX features

### Migration Order

1. Ansible Playbooks (website_https.yml, poodle_fix.yml) - low risk, already in Ansible format
2. Testing Framework - replace Test Kitchen with Molecule
3. InSpec Tests - convert to Ansible assertions or Molecule verifiers
4. Chef Deployment Scripts - create equivalent Ansible playbooks for AWX/Tower deployment

### Assumptions

1. The primary use case is compliance testing of Ansible-managed infrastructure
2. No Chef cookbooks are actively being used for configuration management
3. The InSpec tests are used primarily for validation rather than as part of a larger compliance framework
4. The deployment scripts are used for setting up test environments rather than production infrastructure
5. No external data sources or complex integrations are present
6. No custom InSpec resources are being used that would require special handling
7. The target environment will continue to be Ubuntu 20.04 or compatible systems
8. The migration will maintain the same level of security validation
9. The current setup is used for demonstration/educational purposes rather than production workloads