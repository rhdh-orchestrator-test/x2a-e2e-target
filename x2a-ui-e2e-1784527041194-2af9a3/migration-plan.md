# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec testing. The migration scope is relatively small, focusing on two main components:

1. Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks
2. Existing Ansible playbooks with Chef InSpec testing that need to be standardized and integrated into a unified Ansible framework

The migration complexity is **LOW to MEDIUM** with an estimated timeline of 1-2 weeks, as the repository primarily contains deployment scripts and simple Ansible playbooks with InSpec tests rather than complex Chef cookbooks.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for deploying a secure HTTPS website with Chef InSpec testing
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL/TLS security settings, InSpec compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server setup, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration consideration: Replace with Ansible Molecule for testing.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying an HTTPS website. Migration consideration: Maintain as-is but standardize with Ansible best practices.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability. Migration consideration: Integrate into main website playbook as a security role.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for HTTPS website. Migration consideration: Convert to Ansible Molecule tests or maintain InSpec integration.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security. Migration consideration: Convert to Ansible Molecule tests or maintain InSpec integration.
- `setup-automate/deploy-automate.sh`: Bash script for Chef Automate deployment. Migration consideration: Convert to Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for Chef Infra Server deployment. Migration consideration: Convert to Ansible playbook.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and Apache package version in website_https.yml)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible playbook that configures equivalent monitoring/compliance solution
- **Chef Infra Server**: Replace with Ansible AWX/Tower or alternative configuration management approach
- **Chef InSpec**: Options include:
  1. Maintain InSpec for compliance testing alongside Ansible
  2. Replace with Ansible Molecule for testing
  3. Use alternative compliance tools like OpenSCAP with Ansible integration

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the secure TLS 1.2 configuration and disable insecure protocols (as seen in poodle_fix.yml)
- **SSH Security**: Maintain SSH hardening configurations from the InSpec profile
- **Certificate Management**: Ensure proper handling of SSL certificates (currently self-signed in the Ansible playbook)
- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - SSL certificate generation and storage
  - Recommendation: Implement Ansible Vault for all credentials

### Technical Challenges

- **Chef Automate Replacement**: Determining the appropriate Ansible-compatible replacement for Chef Automate's compliance and monitoring features
- **InSpec Testing Integration**: Deciding whether to maintain InSpec testing or migrate to Ansible-native testing tools
- **Compliance Reporting**: Ensuring compliance reporting capabilities are maintained in the new Ansible-based solution

### Migration Order

1. **Ansible Playbooks** (chef-and-ansible directory): Low risk as they're already in Ansible format, just need standardization
   - Standardize existing playbooks with Ansible best practices
   - Integrate poodle_fix.yml into the main website_https.yml playbook as a role
   - Update testing framework (decide on InSpec vs. Molecule)

2. **Chef Deployment Scripts** (setup-automate directory): Medium complexity
   - Convert deploy-chef-server.sh to an Ansible playbook
   - Convert deploy-automate.sh to an Ansible playbook
   - Implement Ansible Vault for credential management

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being a production deployment
2. The Chef Automate and Chef Infra Server deployment is for demonstration purposes
3. The target environment is Ubuntu 20.04 running on Vagrant VMs
4. There are no complex Chef cookbooks or recipes that need migration, only deployment scripts
5. The organization wants to standardize on Ansible rather than maintaining a hybrid Chef/Ansible environment
6. The InSpec testing capabilities are still desired in the migrated solution
7. The hardcoded credentials in the deployment scripts are for demonstration only and will be replaced with proper secret management