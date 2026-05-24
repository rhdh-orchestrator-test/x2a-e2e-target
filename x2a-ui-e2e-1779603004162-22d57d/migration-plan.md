# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while maintaining the existing Ansible playbooks. Additionally, there are Chef server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https_verify**:
    - Description: InSpec tests for verifying HTTPS website functionality, including port listening, content verification, and SSL protocol checks
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port verification, HTTP response validation, SSL protocol validation

- **ssh_profile**:
    - Description: InSpec compliance profile for SSH security configuration validation, specifically checking root login settings
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, CCI compliance mapping, STIG validation

- **chef-server-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash with Chef server CLI tools
    - Key Features: User creation, organization setup, system configuration

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `website_https.yml`: Ansible playbook for setting up an HTTPS website with Apache. No migration needed as it's already in Ansible format.
- `poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities in Apache. No migration needed as it's already in Ansible format.
- `index.html`: Simple HTML file used for testing. No migration needed.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for both on-premises and cloud deployment (based on comments in deployment scripts)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing
  - Option 4: Maintain InSpec but call it from Ansible using the `command` or `shell` module

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Server CLI Tools**: Replace with Ansible modules for configuration management

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL certificate generation and configuration. Migration should maintain secure defaults (TLSv1.2+).
  - Migration approach: Maintain the same security settings in Ansible playbooks

- **SSH Security**: The InSpec tests validate SSH security configurations.
  - Migration approach: Convert to Ansible-compatible tests while maintaining the same security checks

- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password) should be moved to Ansible Vault
  - SSL certificates and keys are generated dynamically but should be handled securely in Ansible

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks while maintaining the same level of compliance validation.
  - Mitigation: Consider using Ansible's assert module combined with command/shell modules to run similar checks

- **Chef Server Deployment**: Converting Chef server deployment scripts to Ansible playbooks.
  - Mitigation: Create Ansible roles that perform equivalent system configuration and use Ansible's URI module to interact with Chef APIs where necessary

### Migration Order

1. **website_https.yml and poodle_fix.yml**: Already in Ansible format, no migration needed
2. **InSpec Tests**: Convert to Ansible-compatible testing framework
   - Start with website_https_verify.rb (simpler)
   - Then migrate ssh_profile.rb (more complex with compliance mappings)
3. **Chef Server Deployment Scripts**: Convert to Ansible playbooks
   - Create roles for system configuration
   - Create tasks for Chef server installation and configuration

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, not to provide production-ready infrastructure code.
2. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) are already in the desired format and don't need migration.
3. The deployment scripts are used for setting up test environments and contain simplified configurations not intended for production use (e.g., hardcoded passwords).
4. The target audience for this migration is familiar with both Chef and Ansible concepts.
5. The InSpec tests are intended to be run against systems managed by Ansible, demonstrating a hybrid approach to infrastructure management and compliance testing.
6. The repository is primarily educational/demonstrative in nature rather than representing a complete production infrastructure.