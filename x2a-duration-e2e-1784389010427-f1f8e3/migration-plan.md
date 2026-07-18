# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations that need to be consolidated into a unified Ansible approach. The repository primarily consists of:

1. Chef Automate and Chef Infra Server deployment scripts
2. Ansible playbooks for configuring HTTPS websites with Apache
3. InSpec tests for compliance verification

The migration complexity is relatively low as most of the configuration is already in Ansible format. The primary focus will be on replacing the Chef server deployment scripts with Ansible equivalents and ensuring the InSpec tests can be integrated into an Ansible-based workflow. Estimated timeline: 1-2 weeks for a complete migration.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for configuring HTTPS websites with Apache and InSpec tests for compliance verification
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL/TLS security settings, InSpec compliance tests

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server setup, user and organization creation

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook for configuring Apache with HTTPS. Migration considerations: Already in Ansible format, can be used as-is with minor adjustments.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities. Migration considerations: Already in Ansible format, can be used as-is.
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing. Migration considerations: Update to use Ansible-native testing tools or adapt for continued use with InSpec.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for HTTPS website verification. Migration considerations: Integrate with Ansible testing workflow.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Migration considerations: Integrate with Ansible testing workflow.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate. Migration considerations: Replace with Ansible playbook for infrastructure setup.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Migration considerations: Replace with Ansible playbook for infrastructure setup.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and Apache package version in website_https.yml)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for infrastructure management
- **Chef Infra Server**: Replace with Ansible inventory and configuration management
- **InSpec**: Integrate with Ansible using ansible-lint and molecule for testing, or maintain InSpec as a complementary testing tool

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the secure TLS 1.2 configuration and disabled SSL3 as verified in the InSpec tests
- **SSH Security**: Maintain SSH hardening configurations as specified in the InSpec tests
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates are generated dynamically in the playbook, which is a good practice to maintain

### Technical Challenges

- **InSpec Integration**: Determining how to integrate InSpec tests with Ansible workflow. Mitigation: Use Ansible's built-in testing capabilities or integrate InSpec as a post-deployment verification step.
- **Chef Server Replacement**: Replacing Chef server functionality with Ansible equivalents. Mitigation: Use Ansible AWX/Tower for web UI and role-based access control.

### Migration Order

1. `chef-and-ansible/website_https.yml` and `chef-and-ansible/poodle_fix.yml` (low risk, already in Ansible format)
2. InSpec tests integration with Ansible workflow (moderate complexity)
3. Chef Automate and Chef Infra Server deployment scripts (high complexity, requires complete rewrite)

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production, as indicated by the README.md mentioning "working examples" and "how-tos".
2. The InSpec tests are intended to be run against systems configured by Ansible, not Chef.
3. The Chef server deployment scripts are used for setting up a Chef infrastructure that is not directly related to the Ansible playbooks in the repository.
4. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with secure values in a production environment.
5. The target environment is Ubuntu 20.04 running on Vagrant VMs for testing purposes.