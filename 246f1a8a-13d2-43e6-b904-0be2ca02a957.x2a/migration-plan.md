# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server setup scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving the existing Ansible playbooks while standardizing their structure
3. Maintaining the Chef InSpec tests for compliance validation

**Estimated Timeline**: 1-2 weeks for a single engineer, including testing and documentation.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https-configuration**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support, including SSL certificate generation and virtual host configuration
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Self-signed certificate generation, Apache virtual host configuration, website deployment

- **poodle-vulnerability-fix**:
    - Description: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2 in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server on a single node
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying standalone Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test to verify HTTPS website configuration
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server CLI**: Replace with Ansible roles for configuration management
- **Test Kitchen with Ansible**: Migrate to Ansible Molecule for testing
- **InSpec**: Maintain InSpec tests but integrate with Ansible using ansible_inspec module or convert to Ansible assert modules

### Security Considerations

- **SSL/TLS Configuration**: The poodle_fix.yml playbook enforces TLSv1.2 only. This should be preserved in the migrated solution.
- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates. Consider enhancing with Let's Encrypt integration.
- **SSH Hardening**: The ssh_profile.rb InSpec test checks for SSH root login disablement. Ensure this security check is maintained.
- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Recommend migrating to Ansible Vault for secure credential storage

### Technical Challenges

- **Chef Server User Management**: The Chef server deployment scripts create users and organizations. This functionality needs to be replicated in Ansible, potentially using the community.general.chef_user and community.general.chef_org modules.
- **System Tuning**: The Chef deployment scripts set specific kernel parameters (vm.max_map_count, vm.dirty_expire_centisecs). These need to be properly configured in the Ansible equivalent.
- **InSpec Integration**: Maintaining the InSpec tests while moving to an Ansible-only workflow will require setting up proper test hooks.

### Migration Order

1. **chef-and-ansible Ansible Playbooks** (low risk, already in Ansible format)
   - Standardize and optimize existing Ansible playbooks
   - Implement Ansible best practices (roles, variables, etc.)

2. **InSpec Tests** (moderate complexity)
   - Integrate existing InSpec tests with Ansible workflow
   - Consider adding Ansible-native assertions as alternatives

3. **Chef Deployment Scripts** (high complexity)
   - Create Ansible roles for Chef Automate and Chef Server deployment
   - Implement secure credential management with Ansible Vault

### Assumptions

1. The repository is primarily used for demonstration/educational purposes rather than production deployment, based on the README stating it provides "working examples of Chef related to content created by the Technical Product Marketing and Developer Relations teams."

2. The Chef InSpec tests are intended to be preserved as they demonstrate compliance automation alongside Ansible (as mentioned in the chef-and-ansible README).

3. The hardcoded credentials in the deployment scripts are for demonstration purposes only and would be replaced with secure alternatives in a production environment.

4. The target environment is Ubuntu 20.04 based on the kitchen.yml configuration, though the deployment scripts may work on other Linux distributions.

5. The migration will maintain the same functionality but improve security practices and follow Ansible best practices.