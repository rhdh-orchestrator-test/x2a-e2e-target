# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Two Ansible playbooks for configuring HTTPS websites and fixing SSL vulnerabilities
2. Chef InSpec test profiles for verifying compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks to fully migrate all components to pure Ansible solutions. The primary focus will be on replacing Chef InSpec with Ansible-native testing solutions while preserving the compliance automation capabilities.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https-configuration**:
    - Description: Ansible playbook that configures Apache with HTTPS, creates self-signed certificates, and deploys a simple website
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle-vulnerability-fix**:
    - Description: Ansible playbook that remediates the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **https-compliance-tests**:
    - Description: Chef InSpec tests that verify HTTPS configuration and SSL protocol security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening checks, HTTPS response validation, SSL protocol verification

- **ssh-compliance-profile**:
    - Description: Chef InSpec profile that verifies SSH security configuration compliance with security standards
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance tagging (STIG, CCI references)

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

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests - will need to be replaced with Ansible-native testing framework
- `index.html`: Simple HTML file used as a template for website deployment - can be preserved as-is or converted to an Ansible template

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 LTS (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible Molecule for infrastructure testing
  - Option 2: Ansible Lint for static code analysis
  - Option 3: Integration with OpenSCAP for compliance testing
  - Option 4: Maintain InSpec as a standalone tool called from Ansible

- **Test Kitchen**: Replace with:
  - Ansible Molecule for testing infrastructure
  - GitHub Actions or other CI/CD pipeline for automated testing

- **Chef Automate/Server**: Replace deployment scripts with:
  - Ansible roles for compliance scanning and reporting
  - AWX/Ansible Tower for centralized management
  - Compliance as Code approach using Ansible collections

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Approach: Convert to an Ansible role with appropriate defaults and variables
  - Ensure idempotent SSL protocol configuration

- **Compliance Testing**: The InSpec tests contain important security checks
  - Approach: Convert InSpec tests to Ansible assert tasks or Molecule verify tests
  - Preserve compliance metadata (STIG IDs, CCI references) in Ansible documentation

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - SSL certificates should be managed securely, potentially with ansible-vault or external secret management

### Technical Challenges

- **Compliance Testing Framework**: Chef InSpec provides rich compliance testing capabilities
  - Mitigation: Evaluate Ansible Molecule, OpenSCAP integration, or maintaining InSpec as a standalone tool
  - Document test coverage gaps if any exist after migration

- **Test Kitchen Integration**: The current setup uses Test Kitchen to orchestrate testing
  - Mitigation: Implement equivalent testing workflow with Ansible Molecule
  - Ensure test environments match the original configuration

- **Chef Server Functionality**: The deployment scripts set up Chef Server infrastructure
  - Mitigation: Determine if Chef Server functionality is needed or if it can be replaced with Ansible Tower/AWX
  - Document any Chef-specific features that may not have direct Ansible equivalents

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format
   - Convert to Ansible roles with proper structure
   - Implement variable parameterization for better reusability
   - Add documentation

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity
   - Convert to Ansible assert tasks or Molecule tests
   - Preserve compliance metadata and test coverage
   - Validate against original test scenarios

3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity
   - Determine if Chef Server/Automate functionality is still required
   - If yes, create Ansible roles to deploy these components
   - If no, implement equivalent functionality in Ansible/AWX

4. **Testing Framework** (kitchen.yml): Moderate complexity
   - Replace with Ansible Molecule configuration
   - Ensure test environments match original specifications
   - Implement CI/CD integration

### Assumptions

1. The primary purpose of this repository is to demonstrate compliance automation with Chef InSpec alongside Ansible, not to provide production infrastructure
2. The Chef Automate and Chef Server deployment scripts are examples and not critical production components
3. The compliance tests (InSpec profiles) contain the most valuable intellectual property in terms of security standards
4. Ubuntu 20.04 LTS will remain the target operating system
5. The migration will prioritize maintaining the same level of compliance testing coverage
6. No external data sources or integrations are present that would complicate the migration
7. The current setup is used for testing and demonstration, not for managing production infrastructure