# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations that need to be consolidated into a unified Ansible approach. The repository primarily consists of:

1. Chef Automate and Chef Infra Server deployment scripts
2. Ansible playbooks for configuring HTTPS websites with Apache
3. Chef InSpec tests for compliance verification

The migration complexity is relatively low as most of the configuration is already in Ansible format. The primary focus will be on replacing the Chef Automate and Chef Infra Server deployment scripts with equivalent Ansible roles and playbooks, and ensuring the InSpec tests can be integrated into an Ansible-based workflow.

Estimated timeline: 1-2 weeks for a complete migration, with the majority of time spent on creating Ansible equivalents for the Chef server deployment scripts.

## Module Migration Plan

This repository contains Chef and Ansible configurations that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for configuring HTTPS websites with Apache and InSpec tests for compliance verification
    - Path: chef-and-ansible
    - Technology: Ansible + Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL/TLS security settings, compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash + Chef
    - Key Features: Chef server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook that configures an Apache web server with HTTPS support. Migration considerations include preserving the SSL certificate generation and virtual host configuration.
  
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook that addresses the POODLE vulnerability by updating SSL configuration in Apache. Migration considerations include ensuring this security fix is incorporated into the main Apache configuration role.
  
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec. Migration considerations include replacing with molecule for Ansible role testing or adapting to continue using InSpec with Ansible.
  
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality. Migration considerations include converting to Ansible test framework or maintaining InSpec integration.
  
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Migration considerations include converting to Ansible test framework or maintaining InSpec integration.
  
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Migration considerations include creating an Ansible role to replace this functionality if still needed.
  
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Migration considerations include creating an Ansible role to replace this functionality if still needed.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and Apache package version in website_https.yml)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, but the scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server CLI**: Replace with Ansible roles for configuration management
- **Chef InSpec**: Either maintain as a compliance tool used alongside Ansible or replace with Ansible-native testing frameworks like Molecule

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in poodle_fix.yml that enforces TLSv1.2
- **SSH Security**: The InSpec profile for SSH security must be maintained or converted to equivalent Ansible checks
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates are generated dynamically but should be managed securely in the migrated solution

### Technical Challenges

- **InSpec Integration**: Determining whether to maintain InSpec for compliance testing or migrate to Ansible-native testing tools
- **Chef Server Deployment**: If Chef Server is still needed in the environment, creating an equivalent Ansible role for deployment
- **Test Kitchen Replacement**: Replacing Test Kitchen with Molecule or another Ansible-native testing framework

### Migration Order

1. **chef-and-ansible/website_https.yml and poodle_fix.yml** (low risk, already in Ansible format)
2. **InSpec tests** (moderate complexity, decide on testing strategy)
3. **Chef deployment scripts** (high complexity, requires creating new Ansible roles)

### Assumptions

1. The Chef Automate and Chef Infra Server deployment scripts may no longer be needed if the entire infrastructure is being migrated to Ansible. If they are still required, they will need to be converted to Ansible roles.
2. The InSpec tests are valuable for compliance verification and should be maintained, either by integrating with Ansible or converting to equivalent Ansible tests.
3. The target environment will continue to be Ubuntu 20.04 or a compatible Linux distribution.
4. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be replaced with secure credential management in the migrated solution.
5. The Apache HTTPS configuration is a critical component that must be preserved in the migration.