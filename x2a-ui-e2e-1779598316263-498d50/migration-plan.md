# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing rather than being a pure Chef cookbook repository. Additionally, there are shell scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible components are already in place. The primary migration tasks will involve:
1. Converting the Chef InSpec tests to Ansible-native testing solutions
2. Adapting the Chef Automate and Chef Infra Server deployment scripts to Ansible playbooks

**Estimated Timeline**: 1-2 weeks for a complete migration, with minimal complexity due to the limited scope of Chef-specific components.

## Module Migration Plan

This repository contains Chef InSpec tests and shell scripts that need individual migration planning:

### MODULE INVENTORY

- **chef-inspec-tests**:
    - Description: Chef InSpec tests for verifying HTTPS website configuration and SSH security settings
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: HTTPS verification, SSL/TLS protocol validation, SSH configuration compliance checks

- **chef-automate-deployment**:
    - Description: Shell scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification. Migration consideration: Replace with Ansible Molecule for testing.
- `website_https.yml`: Ansible playbook for setting up an HTTPS website. No migration needed as it's already in Ansible format.
- `poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities. No migration needed as it's already in Ansible format.
- `index.html`: Sample HTML file used by the website playbook. No migration needed.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment (based on comments in setup scripts)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic compliance checks
  - Option 2: Integrate with Ansible Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks
  - Option 4: Consider OpenSCAP integration for compliance scanning

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

### Security Considerations

- **SSH Configuration Testing**: The SSH profile tests for root login restrictions need to be migrated to Ansible-native tests
  - Migration approach: Convert to Ansible assert tasks or Molecule verify phase tests

- **SSL/TLS Security Testing**: Tests for SSL/TLS protocols need to be migrated
  - Migration approach: Use Ansible's uri module with appropriate SSL parameters for verification

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates are generated dynamically in the playbook, which is a good practice to maintain

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's testing syntax to equivalent Ansible assertions may require additional logic
  - Mitigation: Use Ansible's assert module with appropriate conditions, or consider maintaining InSpec for testing while using Ansible for configuration management

- **Chef Server Deployment**: The Chef Server deployment scripts need to be converted to Ansible playbooks
  - Mitigation: Create equivalent Ansible roles for server deployment, potentially using the `command` module to execute Chef-specific commands during transition

### Migration Order

1. **Ansible Testing Framework** (Priority 1): Set up Ansible Molecule to replace Test Kitchen
2. **InSpec Test Conversion** (Priority 2): Convert InSpec tests to Ansible assertions or Molecule verify tests
3. **Chef Deployment Scripts** (Priority 3): Convert Chef Automate and Chef Infra Server deployment scripts to Ansible playbooks

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being a production Chef cookbook repository
2. The target environment is Ubuntu 20.04 as specified in the kitchen.yml file
3. Vagrant is used for local development/testing environments
4. The deployment scripts are intended for demonstration purposes and may need additional security hardening for production use
5. The hardcoded credentials in the deployment scripts are for demonstration only and would be replaced with secure alternatives in production
6. The repository does not contain actual Chef cookbooks that need migration, only InSpec tests and deployment scripts
7. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) are already functioning correctly and don't require migration