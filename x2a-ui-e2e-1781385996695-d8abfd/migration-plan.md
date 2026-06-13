# MIGRATION FROM CHEF/INSPEC TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks demonstrating how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on two main components:

1. Chef InSpec tests for compliance verification
2. Chef Automate/Chef Server deployment scripts

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks for a single developer. The primary focus will be on replacing InSpec tests with Ansible-compatible testing frameworks while preserving the existing Ansible playbooks.

## Module Migration Plan

This repository contains Chef InSpec tests and Chef server deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **chef-inspec-tests**:
    - Description: InSpec tests for verifying HTTPS website configuration and SSH security compliance
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: SSL/TLS protocol verification, SSH configuration compliance checks, web server response testing

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: User creation, organization setup, Chef server configuration

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification. Will need to be replaced with Ansible-native testing framework configuration.
- `website_https.yml`: Ansible playbook for configuring Apache with HTTPS. Can be preserved as-is in the migration.
- `poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability. Can be preserved as-is in the migration.
- `index.html`: Simple HTML file used for testing. Can be preserved as-is.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Molecule for Ansible role testing with testinfra for verification
  - Option 2: Ansible Test modules for integration testing
  - Option 3: Maintain InSpec as a separate tool but integrate with Ansible workflows

- **Test Kitchen**: Replace with Molecule for Ansible role testing and development

- **Chef Automate/Server**: Replace deployment scripts with Ansible playbooks for setting up alternative compliance and automation tools:
  - Option 1: AWX/Ansible Tower for automation
  - Option 2: Compliance as Code using OpenSCAP with Ansible

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the POODLE fix playbook, ensuring TLS 1.2 is enforced
- **SSH Hardening**: The SSH compliance profile must be converted to equivalent Ansible checks
- **Secrets Management**: 
  - Hardcoded credentials in the Chef deployment scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **Test Framework Conversion**: Converting InSpec tests to an Ansible-compatible testing framework will require careful mapping of test assertions
  - Mitigation: Create a mapping document for InSpec resources to testinfra or other Ansible-compatible test assertions
  
- **Compliance Verification**: Ensuring the same level of compliance verification without InSpec
  - Mitigation: Evaluate OpenSCAP, Ansible security roles, or maintaining InSpec as a standalone tool called from Ansible

- **Chef Server Replacement**: Determining the appropriate replacement for Chef Server functionality
  - Mitigation: Document the specific Chef Server features being used and map to Ansible Tower/AWX capabilities

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they can be preserved as-is
2. **InSpec Tests**: Moderate complexity, convert to Ansible-compatible testing framework
3. **Chef Deployment Scripts**: Higher complexity, replace with Ansible playbooks for alternative tools

### Assumptions

1. The primary purpose of this repository is demonstrating InSpec with Ansible rather than production deployment
2. No external dependencies or integrations beyond what's visible in the repository
3. No custom InSpec resources or complex test logic beyond what's shown in the test files
4. The deployment scripts are examples and not used in production environments
5. No specific compliance frameworks or regulatory requirements beyond the basic security checks shown
6. The SSH profile is a standalone example and not part of a larger compliance framework
7. The hardcoded credentials in deployment scripts are for demonstration purposes only