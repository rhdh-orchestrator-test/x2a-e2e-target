# MIGRATION FROM CHEF DEPLOYMENT SCRIPTS TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef Automate/Infra Server deployment scripts, along with Chef InSpec tests for compliance validation. The repository does not contain traditional Chef cookbooks (no recipes/default.rb files), Puppet modules (no manifests/init.pp files), or PowerShell modules (no .psd1 files).

The migration scope is focused on converting the Chef Automate and Chef Infra Server deployment scripts to Ansible playbooks while maintaining the existing Ansible playbooks and InSpec tests. Given the limited scope and small number of files, this migration is estimated to be a low-complexity effort that could be completed within 1-2 weeks, including testing and documentation.

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

**Note: No traditional Chef cookbooks (recipes/default.rb), Puppet modules (manifests/init.pp), or PowerShell modules (.psd1) were found in this repository.**

The repository contains the following components:

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support, including self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate the POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2 for security

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test to verify HTTPS website functionality and security
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test to verify SSH security configuration
- `chef-and-ansible/index.html`: Sample HTML file used for testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible playbooks that configure equivalent monitoring and compliance solutions
- **Chef Infra Server**: Replace with Ansible inventory and configuration management
- **Test Kitchen**: Consider migrating to Ansible Molecule for testing or maintain Test Kitchen with Ansible provisioner
- **InSpec**: Maintain InSpec for compliance testing, as it works well with Ansible

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable insecure protocols. This security hardening should be preserved in the migration.
- **SSH Hardening**: The InSpec profile checks for secure SSH configuration. Ensure Ansible continues to enforce these security controls.
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates are generated as part of the playbook execution

### Technical Challenges

- **Chef Automate Replacement**: Determining the appropriate Ansible-compatible alternatives for Chef Automate's compliance and reporting features
- **InSpec Integration**: Ensuring continued integration between Ansible and InSpec for compliance testing
- **Test Kitchen**: Deciding whether to maintain Test Kitchen with the Ansible provisioner or migrate to Ansible Molecule

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): These are already in Ansible format and only need review and potential optimization
2. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Convert these to Ansible playbooks
3. **Testing Framework**: Update the testing approach to work with the new fully-Ansible implementation

### Assumptions

1. The primary goal is to move away from Chef Automate/Infra Server while maintaining the compliance testing capabilities of InSpec
2. The existing Ansible playbooks are working correctly and don't require significant changes
3. The target environment will continue to be Ubuntu 20.04 or compatible systems
4. Vagrant will continue to be used for development/testing environments
5. The hardcoded credentials in the deployment scripts are for demonstration purposes only and will be replaced with secure alternatives in the production implementation

## Detailed Migration Tasks

### 1. Ansible Playbook Review and Optimization

- Review existing Ansible playbooks for best practices
- Update any deprecated syntax or modules
- Consider breaking down the website_https.yml playbook into roles for better organization
- Ensure idempotence in all playbooks

### 2. Chef Deployment Script Conversion

- Create Ansible playbooks to replace the Chef Automate and Chef Infra Server deployment scripts
- Research and implement Ansible-compatible alternatives for Chef Automate features
- Use Ansible Vault for credential management
- Document the new deployment process

### 3. Testing Framework Updates

- Update kitchen.yml to work with the new fully-Ansible implementation
- Consider implementing Ansible Molecule as an alternative testing framework
- Ensure InSpec tests continue to work with the new implementation

### 4. Documentation

- Update all documentation to reflect the new Ansible-only approach
- Create a migration guide for users of the original repository
- Document the integration between Ansible and InSpec for compliance testing

## Timeline Estimate

- **Phase 1 - Planning and Setup**: 1-2 days
- **Phase 2 - Ansible Playbook Review**: 1-2 days
- **Phase 3 - Chef Deployment Script Conversion**: 3-5 days
- **Phase 4 - Testing Framework Updates**: 2-3 days
- **Phase 5 - Documentation**: 1-2 days
- **Phase 6 - Testing and Validation**: 2-3 days

**Total Estimated Time**: 10-17 days (2-3.5 weeks)