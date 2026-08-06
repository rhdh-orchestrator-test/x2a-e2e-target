# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components that need to be migrated to a pure Ansible solution. The repository primarily consists of:

1. Ansible playbooks for configuring web servers with HTTPS
2. Chef InSpec tests for validating configurations
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is **MEDIUM** with an estimated timeline of 2-3 weeks. The primary focus will be on preserving the compliance testing functionality while standardizing on Ansible for all configuration management.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Shell Script
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Shell Script
    - Key Features: Chef Server installation, user and organization creation

- **website-https-compliance**:
    - Description: Chef InSpec profile for validating HTTPS configuration
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh-compliance**:
    - Description: Chef InSpec profile for validating SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification. Migration will require converting to Ansible Molecule for testing.
- `chef-and-ansible/index.html`: Sample HTML file used for testing web server configuration. Can be preserved as-is or incorporated into Ansible templates.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible Molecule with Testinfra for infrastructure testing
  - Option 2: Maintain InSpec as a standalone tool but invoke it from Ansible
  - Option 3: Convert InSpec tests to equivalent Ansible assert tasks

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace with:
  - AWX/Ansible Tower for orchestration
  - Ansible content collections for configuration management
  - Compliance automation using OpenSCAP or Ansible Security Automation

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the POODLE fix playbook
  - Approach: Convert the existing Ansible task to an Ansible role with proper documentation
  - Ensure the SSL protocol restrictions are maintained (TLSv1.2 only)

- **SSH Hardening**: The SSH compliance profile checks for root login restrictions
  - Approach: Create an Ansible role for SSH hardening that implements the same controls
  - Add Ansible assert tasks to validate the configuration

- **Credentials Management**: The deployment scripts contain hardcoded credentials
  - Identified credentials: 1 username/password pair in each deployment script
  - Approach: Replace with Ansible Vault for secure credential storage
  - Remove hardcoded passwords from scripts and use variables from encrypted sources

### Technical Challenges

- **Compliance Testing**: Converting InSpec tests to Ansible-native testing
  - Mitigation: Use Ansible's assert module for basic tests, consider maintaining InSpec for complex compliance testing if needed
  - Create a wrapper playbook that can run compliance checks and report results

- **Chef Automate Replacement**: Finding equivalent functionality in Ansible ecosystem
  - Mitigation: Map Chef Automate features to AWX/Tower features
  - Implement GitOps workflow with CI/CD for configuration management
  - Use collections from Ansible Galaxy to replace Chef cookbook functionality

- **Test Workflow**: Recreating the test workflow currently handled by Test Kitchen
  - Mitigation: Implement Ansible Molecule for testing with similar capabilities
  - Create documentation for developers on the new testing approach

### Migration Order

1. **website-https playbook** (low risk, already in Ansible)
   - Review and refactor into a proper Ansible role structure
   - Add documentation and variables for flexibility

2. **poodle-fix playbook** (low risk, already in Ansible)
   - Incorporate into a security hardening role
   - Add additional SSL/TLS hardening measures

3. **InSpec tests** (moderate complexity)
   - Convert to Ansible assert tasks or Molecule tests
   - Ensure all compliance checks are preserved

4. **Chef deployment scripts** (high complexity)
   - Replace with Ansible playbooks for AWX/Tower deployment
   - Implement secure credential handling

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than for production use
2. The hardcoded credentials in deployment scripts are examples and not used in production
3. The SSL configuration is meant as a security example rather than a complete security implementation
4. The target environment is Ubuntu 20.04 as specified in the kitchen.yml file
5. The repository is used for educational/demonstration purposes based on the README content
6. There are no external dependencies or integrations beyond what's visible in the repository
7. The deployment scripts are intended for on-premises or cloud VM deployment
8. The compliance profiles are examples and not part of a larger compliance framework