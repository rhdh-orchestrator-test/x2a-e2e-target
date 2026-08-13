# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec testing. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving existing Ansible playbooks with InSpec testing capabilities
3. Ensuring compliance automation remains intact during migration

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium - The repository contains minimal Chef-specific code, with most infrastructure already defined in Ansible

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys a secure Apache web server with SSL configuration
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: SSL certificate generation, Apache configuration, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **chef-automate-deploy**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user creation, organization setup

- **chef-server-deploy**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user creation, organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `tests/website_https_verify.rb`: InSpec test profile for verifying HTTPS website deployment
- `tests/ssh_profile.rb`: InSpec test profile for SSH security compliance

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Retain as a compliance testing tool, integrate with Ansible using the ansible_inspec module or through CI/CD pipeline
- **Test Kitchen**: Replace with Ansible Molecule for testing or adapt kitchen.yml to work with pure Ansible
- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that achieve the same server setup

### Security Considerations

- **SSL Configuration**: The migration must preserve the SSL security configurations in the Apache setup
  - Migration approach: Maintain the same OpenSSL certificate generation in Ansible playbooks
  
- **SSH Hardening**: The SSH compliance profile must be maintained
  - Migration approach: Keep InSpec tests and ensure Ansible configurations meet the same security standards

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec Integration**: Ensuring InSpec tests continue to work with pure Ansible deployments
  - Mitigation: Use ansible_inspec module or integrate InSpec tests in CI/CD pipeline

- **Chef Server Replacement**: Determining if Chef Server functionality needs to be replaced
  - Mitigation: Evaluate if Chef Server is needed or if Ansible can fully replace its functionality

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk, already in Ansible format
   - Update to follow current Ansible best practices
   - Ensure compatibility with newer Ansible versions
   - Maintain InSpec test integration

2. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh) - Medium complexity
   - Convert to Ansible playbooks
   - Move hardcoded credentials to Ansible Vault
   - Ensure idempotence in the deployment process

3. **Testing Framework** - Low complexity
   - Migrate from Test Kitchen to Ansible Molecule or adapt kitchen.yml
   - Ensure InSpec tests continue to function with new deployment methods

### Assumptions

1. The repository is primarily used for demonstration/example purposes rather than production deployments (based on README content)
2. The Chef Automate and Chef Infra Server deployments are needed in the migrated solution (rather than being replaced entirely)
3. InSpec testing is a critical component that must be preserved in the migration
4. The hardcoded credentials in the deployment scripts are for demonstration purposes only
5. The target environment will continue to be Ubuntu 20.04 or compatible systems
6. The Apache web server configuration represents a typical use case that needs to be preserved