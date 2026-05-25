# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing rather than containing actual Chef cookbooks that need migration. The repository also includes shell scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible components are already in place. The primary work will involve:
1. Ensuring all compliance tests currently in InSpec format are migrated to Ansible-native solutions
2. Converting the Chef Automate and Chef Infra Server deployment scripts to Ansible playbooks
3. Maintaining the existing functionality while consolidating to a pure Ansible solution

Estimated timeline: 1-2 weeks for a small team, given the limited scope of actual Chef-specific code to migrate.

## Module Migration Plan

This repository contains Chef InSpec tests and shell scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https_verify**:
    - Description: InSpec tests for verifying HTTPS website configuration including port listening, content verification, and SSL/TLS protocol validation
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port testing, HTTP response validation, SSL/TLS protocol verification

- **ssh_profile**:
    - Description: InSpec compliance profile for SSH security configuration focusing on root login restrictions
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, CCI compliance mapping, STIG validation

- **chef-automate-deployment**:
    - Description: Shell script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash script
    - Key Features: User creation, organization setup, system configuration

- **chef-server-deployment**:
    - Description: Shell script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash script
    - Key Features: User creation, organization setup, system configuration

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests - will need to be replaced with Ansible-native testing framework
- `website_https.yml`: Ansible playbook for configuring HTTPS website - already in Ansible format, no migration needed
- `poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability - already in Ansible format, no migration needed
- `index.html`: Sample HTML file used in testing - no migration needed

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, though the deployment scripts mention they can be used for on-prem or cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - For infrastructure testing: Use Ansible Molecule with Testinfra or Goss
  - For compliance testing: Consider OpenSCAP with Ansible or ansible-lint with custom rules
  - For continuous validation: Implement Ansible playbooks that perform the same checks as the InSpec profiles

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure code

### Security Considerations

- **SSH Security Controls**: The SSH compliance profile checks need to be implemented as Ansible tasks or roles
  - Migration approach: Create an Ansible role that implements the same SSH hardening controls and verification
  
- **SSL/TLS Configuration**: The HTTPS verification tests need equivalent Ansible tasks
  - Migration approach: Create Ansible tasks to verify SSL/TLS configuration using modules like uri, openssl_certificate_info

- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deployment scripts (username/password)

### Technical Challenges

- **Compliance Mapping**: The InSpec profiles contain specific compliance mappings (CCI, STIG IDs) that need to be preserved
  - Mitigation: Document compliance mappings in Ansible role metadata or comments to maintain traceability

- **Test Result Reporting**: InSpec provides structured test results that may be consumed by other systems
  - Mitigation: Implement custom reporting in Ansible or use a tool like Ansible Tower/AWX for structured reporting

- **Deployment Workflow**: The Chef Automate and Chef Infra Server deployment scripts perform specific steps that need to be carefully replicated
  - Mitigation: Create idempotent Ansible roles that perform the same configuration steps with proper error handling

### Migration Order

1. **SSH Compliance Profile** (low risk, high value) - Create Ansible role for SSH hardening and compliance
2. **HTTPS Website Verification** (low complexity) - Create Ansible tasks for website verification
3. **Chef Server/Automate Deployment Scripts** (high complexity) - Create Ansible playbooks for deployment

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can work alongside Ansible, not to provide Chef cookbooks for migration
2. The deployment scripts are used for setting up test environments rather than production infrastructure
3. There are no external dependencies on Chef-specific features beyond what's visible in the repository
4. The InSpec tests are used for validation only and not for remediation
5. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs
6. No additional Chef cookbooks or recipes exist beyond what's visible in the repository
7. The migration will consolidate to pure Ansible without maintaining Chef InSpec