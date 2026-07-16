# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are bash scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate. The complexity is low to moderate, as the existing Ansible playbooks can be largely reused, while the InSpec tests need to be converted to Ansible-native solutions. Estimated timeline for migration is 1-2 weeks, with most effort focused on replacing InSpec tests with equivalent Ansible functionality.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality of the web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance with security standards (STIG)

- **chef-automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible Molecule for testing.
- `index.html`: Simple HTML file used for testing. Migration consideration: Can be reused as-is or templated in Ansible.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, though the deployment scripts could be used in any cloud environment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - For compliance testing: Use ansible-lint for static analysis
  - For runtime verification: Use Ansible assert module or custom modules
  - For comprehensive compliance: Consider integrating with OpenSCAP or using ansible-lockdown roles

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

### Security Considerations

- **SSL Configuration**: The poodle_fix.yml playbook specifically addresses SSL security. Ensure this security hardening is maintained in the migrated solution.
- **SSH Security**: The ssh_profile.rb InSpec test verifies SSH security configurations. Ensure these checks are implemented in Ansible.
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates are generated during deployment but should be managed securely in production environments

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible verification tasks will require careful mapping of InSpec resources to Ansible modules.
  - Mitigation: Use Ansible's assert module combined with command/shell modules to perform equivalent checks.

- **Chef Automate Deployment**: The Chef Automate and Chef Infra Server deployment scripts need to be replaced with equivalent Ansible roles.
  - Mitigation: Create Ansible roles that perform the same server setup and configuration tasks.

### Migration Order

1. **website_https.yml** (low risk, already Ansible): Review and optimize the existing Ansible playbook
2. **poodle_fix.yml** (low risk, already Ansible): Review and optimize the existing Ansible playbook
3. **website_https_verify.rb** (moderate complexity): Convert InSpec tests to Ansible verification tasks
4. **ssh_profile.rb** (moderate complexity): Convert InSpec compliance tests to Ansible verification tasks
5. **Chef deployment scripts** (high complexity): Create Ansible roles to replace the bash scripts for Chef deployment

### Assumptions

1. The primary goal is to move away from Chef InSpec for testing while maintaining or enhancing the compliance verification capabilities.
2. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) are working correctly and only need minor adjustments.
3. The deployment scripts for Chef Automate and Chef Infra Server are intended to be replaced with Ansible equivalents rather than maintained as-is.
4. The target environment will continue to be Ubuntu 20.04 or compatible systems.
5. There is no requirement to maintain backward compatibility with Chef InSpec.
6. The repository appears to be primarily for demonstration purposes rather than production use, based on the README description.
7. No external inventory or variable files are present, suggesting simple deployment scenarios.
8. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with secure alternatives in production.