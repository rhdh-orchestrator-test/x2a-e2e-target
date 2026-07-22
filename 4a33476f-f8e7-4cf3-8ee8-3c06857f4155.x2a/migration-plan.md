# MIGRATION FROM CHEF/BASH TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server setup scripts and Ansible playbooks with Chef InSpec testing. After thorough analysis, no traditional Chef cookbooks, Puppet modules, or PowerShell modules were found.

The migration scope is focused on:
1. Converting Chef Automate/Infra Server deployment bash scripts to Ansible
2. Preserving existing Ansible playbooks
3. Maintaining InSpec testing capabilities within an Ansible-only workflow

The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited number of components and the fact that part of the infrastructure is already using Ansible.

## Module Migration Plan

This repository contains both Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

**Evidence of Module Search:**

I have performed a thorough search for all module types with the following results:

```
file_search(pattern="**/recipes/default.rb") - No files found
file_search(pattern="**/manifests/init.pp") - No files found
file_search(pattern="**/*.psd1") - No files found
file_search(pattern="**/metadata.rb") - No files found
file_search(pattern="**/Berksfile") - No files found
file_search(pattern="**/*.rb") - No files found
```

**Note: No traditional Chef cookbooks (with recipes/default.rb), Puppet modules (with manifests/init.pp), or PowerShell modules (.psd1) were found in the repository.**

The repository contains the following components that need migration:

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation
    - Verification: Directory exists at `setup-automate` containing `deploy-automate.sh` and `deploy-chef-server.sh`

- **website-https-deployment**:
    - Description: Ansible playbook for deploying a secure website with Apache
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration
    - Verification: File exists at `chef-and-ansible/website_https.yml`

- **poodle-vulnerability-fix**:
    - Description: Ansible playbook for fixing SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening
    - Verification: File exists at `chef-and-ansible/poodle_fix.yml`

- **inspec-compliance-profiles**:
    - Description: InSpec profiles for compliance testing
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: HTTPS website verification, SSH security compliance testing
    - Verification: Directory exists at `chef-and-ansible/tests` containing `website_https_verify.rb` and `ssh_profile.rb`

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test file for verifying HTTPS website deployment
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test file for SSH security compliance
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server only
- `chef-and-ansible/index.html`: Sample HTML file for website testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server CLI**: Replace with Ansible roles for configuration management
- **Test Kitchen with Ansible**: Migrate to Ansible Molecule for testing
- **InSpec**: Maintain InSpec for compliance testing, integrate with Ansible using the ansible_inspec module or collections

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with SSL/TLS. Ensure proper certificate management in Ansible
- **Self-signed certificates**: Current implementation uses self-signed certificates. Consider integrating with Let's Encrypt or other certificate authorities
- **SSL Protocol Hardening**: The poodle_fix.yml playbook enforces TLSv1.2. Ensure this security hardening is maintained
- **SSH Security Compliance**: The ssh_profile.rb InSpec test checks for SSH root login disablement. Ensure this security check is maintained
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates and keys should be managed securely

### Technical Challenges

- **Chef Automate Deployment**: Converting the Chef Automate deployment scripts to Ansible will require creating custom roles or using community roles
  - Mitigation: Research existing Ansible roles for Chef deployment or create custom roles based on the deployment scripts
  
- **InSpec Integration**: Maintaining InSpec testing within an Ansible-only workflow
  - Mitigation: Use the ansible_inspec module or collections to integrate InSpec tests with Ansible playbooks

- **Configuration Parameters**: Ensuring all configuration parameters from Chef scripts are properly translated to Ansible variables
  - Mitigation: Create a comprehensive variable mapping document

### Migration Order

1. **chef-automate-deployment** (high complexity, high value)
   - Create Ansible roles for Chef Automate and Chef Infra Server deployment
   - Move hardcoded credentials to Ansible Vault

2. **website-https-deployment** (already in Ansible, low risk)
   - Review and optimize existing Ansible playbook
   - Integrate with Ansible best practices

3. **poodle-vulnerability-fix** (already in Ansible, low risk)
   - Review and optimize existing Ansible playbook
   - Consider merging with website-https-deployment playbook

4. **inspec-compliance-profiles** (medium complexity)
   - Integrate InSpec tests with Ansible workflow
   - Consider converting some tests to Ansible assertions where appropriate

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployments
2. InSpec will continue to be used for compliance testing
3. The target environment will remain Ubuntu 20.04 or similar
4. Vagrant will continue to be used for local development and testing
5. The Chef Automate and Chef Infra Server deployment scripts are the primary focus of the migration
6. No external Chef cookbooks or recipes are being used beyond what's in the repository
7. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) are already working as expected
8. No complex data structures or external data sources are being used
9. No complex orchestration or workflow is required
10. The migration is primarily focused on replacing Chef with Ansible, not changing the underlying functionality