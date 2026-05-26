# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. There are also Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, as most of the infrastructure code is already in Ansible format, with Chef primarily used for testing and server deployment.

**Estimated Timeline**: 1-2 weeks
**Complexity**: Low to Medium
**Primary Focus**: Converting InSpec tests to Ansible-native testing solutions and replacing Chef server deployment scripts with Ansible equivalents

## Module Migration Plan

This repository contains Chef and Ansible components that need individual migration planning:

### MODULE INVENTORY

- **chef-inspec-tests**:
    - Description: Chef InSpec tests for validating HTTPS website configuration and SSH security settings
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: HTTPS validation, SSL/TLS protocol verification, SSH configuration compliance testing

- **chef-server-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts with Chef server installation
    - Key Features: User creation, organization setup, server configuration

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification. Will need to be replaced with Ansible-native testing framework configuration.
- `website_https.yml`: Ansible playbook for setting up an HTTPS website with Apache. Already in Ansible format, no migration needed.
- `poodle_fix.yml`: Ansible playbook for fixing SSL configuration in Apache to mitigate POODLE vulnerability. Already in Ansible format, no migration needed.
- `index.html`: Simple HTML file used for testing. No migration needed.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be environment-agnostic with potential for both on-premises and cloud deployment (based on comments in deployment scripts)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Replace InSpec tests with Ansible Molecule for infrastructure testing
  - Consider using ansible-lint for static code analysis
  - For compliance testing specifically, consider migrating to OpenSCAP with ansible-collection-compliance

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace server deployment scripts with Ansible roles for:
  - Configuration management server setup (consider AWX/Ansible Tower)
  - User and organization management

### Security Considerations

- **SSH Configuration Testing**: The current InSpec tests verify SSH root login settings. Ensure these compliance checks are maintained in the Ansible migration.
  - Migration approach: Convert to Ansible assert tasks or Molecule verify phase

- **SSL/TLS Security**: The current tests verify proper TLS protocols and disabled SSL3. Maintain these security checks in the Ansible migration.
  - Migration approach: Create equivalent checks using Ansible modules or Molecule verify phase

- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates are generated in the playbook - consider using ansible-vault for storing sensitive key material

### Technical Challenges

- **Compliance Testing Framework**: Chef InSpec provides a domain-specific language for compliance testing that doesn't have a direct equivalent in Ansible. 
  - Mitigation: Use a combination of Ansible assert modules, custom modules, and potentially integrate with tools like OpenSCAP or DISA STIG automation

- **Test Kitchen to Molecule Migration**: The testing workflow will need to be redesigned.
  - Mitigation: Create equivalent Molecule scenarios that match the current Test Kitchen setup

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - Review and ensure `website_https.yml` and `poodle_fix.yml` follow best practices
   - No actual migration needed as these are already Ansible playbooks

2. **InSpec Tests** (Medium complexity)
   - Convert `website_https_verify.rb` and `ssh_profile.rb` to Ansible Molecule tests
   - Ensure all compliance checks are maintained

3. **Chef Server Deployment Scripts** (Medium complexity)
   - Create Ansible roles to replace `deploy-automate.sh` and `deploy-chef-server.sh`
   - Implement proper secret management with Ansible Vault

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being a production infrastructure codebase
2. The deployment scripts are examples and may contain simplified configurations not suitable for production
3. The hardcoded credentials in the deployment scripts are for demonstration purposes only
4. The repository is primarily focused on demonstrating compliance automation rather than complex infrastructure management
5. There are no external dependencies or integrations beyond what's visible in the repository
6. The target environment is Ubuntu 20.04 running on Vagrant VMs
7. There are no specific performance requirements or scaling considerations mentioned
8. The migration will maintain the same functionality but using Ansible-native tools