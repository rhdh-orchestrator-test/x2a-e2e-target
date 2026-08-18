# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate setup scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate and Chef Infra Server deployment scripts to Ansible playbooks
2. Preserving the existing Ansible playbooks that deploy a secure web server
3. Integrating the Chef InSpec tests into an Ansible-native testing framework

**Estimated Timeline**: 1-2 weeks for a single engineer, with the majority of time spent on creating equivalent Ansible roles for Chef Automate deployment.

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys a secure Apache web server with SSL configuration
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `tests/website_https_verify.rb`: InSpec test to verify HTTPS configuration
- `tests/ssh_profile.rb`: InSpec test to verify SSH security configuration

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use ansible-test with custom Python test modules
  - Option 2: Integrate Molecule for testing with testinfra backend
  - Option 3: Keep InSpec as a testing tool but invoke it directly from Ansible

- **Test Kitchen**: Replace with:
  - Option 1: Molecule for Ansible role testing
  - Option 2: Custom Ansible playbook that creates test environments

- **Chef Automate/Infra Server**: Replace with:
  - Option 1: AWX/Ansible Tower for enterprise automation platform
  - Option 2: Ansible Automation Platform
  - Option 3: Custom Ansible playbooks for configuration management without a central server

### Security Considerations

- **SSL Configuration**: The migration must preserve the SSL hardening in the poodle_fix.yml playbook
  - Migration approach: Direct transfer of tasks to new Ansible role with equivalent functionality

- **SSH Hardening**: The SSH security profile tests must be maintained
  - Migration approach: Convert InSpec tests to equivalent Ansible assert statements or testinfra tests

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **Chef Automate Deployment**: Converting the Chef Automate deployment scripts to Ansible requires:
  - Understanding the Chef Automate architecture
  - Creating equivalent Ansible tasks for each deployment step
  - Handling system requirements (vm.max_map_count, vm.dirty_expire_centisecs)
  - Mitigation strategy: Create a dedicated Ansible role for Chef Automate deployment with proper idempotence checks

- **Testing Framework**: Transitioning from InSpec to Ansible-native testing
  - Challenge: InSpec provides domain-specific language for compliance testing
  - Mitigation strategy: Use Ansible assert modules with custom Python scripts for complex tests, or maintain InSpec as a separate tool called from Ansible

### Migration Order

1. **Existing Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk, already in Ansible format
   - Convert to proper Ansible roles with variables
   - Update handlers for better idempotence
   - Fix any deprecated syntax

2. **Testing Framework** - Moderate complexity
   - Convert InSpec tests to Ansible-compatible format
   - Set up Molecule for testing infrastructure
   - Ensure all compliance checks are preserved

3. **Chef Deployment Scripts** - High complexity
   - Create Ansible roles to replace Chef Automate and Chef Server deployment
   - Implement proper secret management with Ansible Vault
   - Add idempotence to ensure scripts can be run multiple times

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployment, based on the README stating it provides "working examples of Chef related to content created by the Technical Product Marketing and Developer Relations teams."

2. The Chef Automate and Chef Server deployment scripts are intended for lab environments, as they contain hardcoded credentials and simplified setup steps.

3. The InSpec tests are essential for compliance verification and must be preserved in functionality, even if the implementation changes.

4. The target environment is Ubuntu 20.04 based on the kitchen.yml configuration, though the deployment scripts might work on other distributions.

5. The migration should preserve the ability to test deployments in a Vagrant environment as currently configured in kitchen.yml.

6. The current implementation uses a mix of technologies (Ansible, Chef, InSpec) intentionally to demonstrate integration patterns, so a complete migration to pure Ansible might not be the original intent of the repository.