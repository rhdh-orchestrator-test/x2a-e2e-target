# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests, along with Chef Automate/Chef Infra Server deployment scripts. The migration scope is relatively small, focusing on converting existing Ansible playbooks to a standardized Ansible structure while preserving the compliance testing capabilities currently provided by Chef InSpec.

**Estimated Timeline**: 1-2 weeks
- 2-3 days for playbook migration and standardization
- 2-3 days for converting InSpec tests to Ansible-compatible testing frameworks
- 2-3 days for testing and validation
- 1-2 days for documentation and knowledge transfer

**Complexity**: Low to Medium
- The existing Ansible playbooks are straightforward and well-structured
- The InSpec tests will need conversion to an Ansible-compatible testing framework
- The Chef Automate/Chef Infra Server deployment scripts will need to be replaced with Ansible roles

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `chef-and-ansible/index.html`: Static HTML file used by the website_https playbook. Can be directly incorporated into Ansible role.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Molecule with Testinfra for infrastructure testing
  - Option 2: Ansible Test for compliance testing
  - Option 3: Continue using InSpec but integrate with Ansible workflow

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - AWX/Tower for orchestration and testing in production-like environments

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for orchestration and management
  - Ansible Collections for role and module management
  - Ansible Vault for secrets management

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Ensure proper SSL/TLS protocols are enforced in the migrated Ansible roles.
  - Migration approach: Create an Ansible role for Apache with SSL that follows current security best practices.

- **SSH Security**: The InSpec tests verify SSH security configurations.
  - Migration approach: Create Ansible roles that enforce SSH security best practices and include idempotent checks.

- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password) should be moved to Ansible Vault.
  - Self-signed certificates should be managed securely, potentially using ansible-vault for private keys.
  - Count of credentials detected: 3 (username, password, SSL private key)

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to an Ansible-compatible testing framework will require mapping InSpec resources to equivalent testing constructs.
  - Mitigation: Use Molecule with Testinfra which has similar syntax and capabilities to InSpec.

- **Chef Automate Replacement**: Replacing Chef Automate functionality with Ansible Tower/AWX.
  - Mitigation: Document the equivalent workflows in Ansible Tower/AWX and create migration guides for users.

- **Testing Framework Integration**: Ensuring that the new testing framework integrates well with CI/CD pipelines.
  - Mitigation: Set up CI/CD pipeline examples using common tools (Jenkins, GitHub Actions) with the new Ansible testing framework.

### Migration Order

1. **website_https playbook** (low risk, already Ansible)
   - Convert to Ansible role structure
   - Implement idempotency improvements
   - Add documentation

2. **poodle_fix playbook** (low risk, already Ansible)
   - Convert to Ansible role structure
   - Combine with website_https role as an optional feature
   - Add documentation

3. **InSpec tests** (medium complexity)
   - Convert to Molecule/Testinfra tests
   - Ensure they validate the same compliance requirements
   - Integrate with CI/CD pipeline

4. **Chef deployment scripts** (high complexity)
   - Create Ansible roles for deploying Ansible AWX/Tower
   - Document migration path from Chef Automate to Ansible AWX/Tower
   - Create data migration utilities if needed

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being production infrastructure code.
2. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions.
3. The self-signed certificates are for demonstration purposes and would be replaced with proper certificates in production.
4. The Chef Automate and Chef Infra Server deployment scripts are intended to be replaced with equivalent Ansible functionality.
5. The current users of this repository are familiar with both Chef and Ansible concepts.
6. The SSH security profile is a general security requirement that should be maintained in the migrated solution.
7. No external data sources or databases are being managed by the current code.
8. The migration will standardize on Ansible best practices including role structure, variable naming, and module usage.