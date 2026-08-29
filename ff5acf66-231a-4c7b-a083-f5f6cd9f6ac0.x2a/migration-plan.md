# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate deployment scripts and Ansible playbooks used for demonstration and educational purposes. The repository appears to be a collection of examples rather than a production infrastructure codebase. The migration scope is relatively small, focusing on standardizing the existing Ansible playbooks and converting the Chef Automate deployment scripts to Ansible.

**Timeline Estimate**: 1-2 weeks for a single engineer to complete the migration, including testing.

## Module Migration Plan

This repository contains both Chef infrastructure setup scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

After thorough examination of the repository using file_search for patterns "**/recipes/default.rb" (Chef cookbooks), "**/manifests/init.pp" (Puppet modules), and "**/*.psd1" (PowerShell modules), no traditional Chef cookbooks, Puppet modules, or PowerShell modules were found.

The repository contains:
- Bash scripts for Chef Automate deployment
- Ansible playbooks
- Test Kitchen configuration
- InSpec tests

No standard modules requiring migration were identified.

### Infrastructure Files

- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server only
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure Apache web server with SSL
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities in Apache
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with Vagrant
- `chef-and-ansible/tests/website_https_verify.rb`: Chef InSpec tests for verifying HTTPS website deployment
- `chef-and-ansible/index.html`: Sample HTML file for website testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (for testing), but production environment not specified
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server CLI**: Replace with Ansible roles for configuration management
- **Test Kitchen**: Consider migrating to Molecule for Ansible role testing
- **InSpec**: Can be retained for compliance testing with Ansible

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Migration should maintain or enhance security settings:
  - Ensure TLS 1.2+ is enforced (as in poodle_fix.yml)
  - Maintain proper certificate generation and deployment
- **Hardcoded Credentials**: The deployment scripts contain hardcoded credentials:
  - In setup-automate scripts: username, password, email
  - These should be moved to Ansible Vault or another secrets management solution
- **Vault/secrets management**:
  - No existing vault implementation detected
  - 5 credential instances found in setup-automate scripts (username, password, email, organization name, hostname)

### Technical Challenges

- **Chef Automate Deployment**: Converting the Chef Automate deployment scripts to Ansible will require:
  - Creating Ansible roles for Chef Automate and Chef Server installation
  - Implementing idempotent checks to prevent reinstallation
  - Handling system requirements (vm.max_map_count, vm.dirty_expire_centisecs)

- **InSpec Integration**: Maintaining the InSpec tests while migrating to pure Ansible:
  - Create an Ansible role that can run InSpec tests
  - Consider using Ansible's assert module for simple tests

### Migration Order

1. **website_https.yml playbook** (low risk, already Ansible)
   - Review and refactor into proper Ansible role structure
   - Move variables to defaults or vars
   - Implement best practices for Ansible

2. **poodle_fix.yml playbook** (low risk, already Ansible)
   - Review and refactor into proper Ansible role structure
   - Consider merging with website-https as a single Apache role

3. **Chef Automate deployment scripts** (high complexity)
   - Create Ansible roles for Chef Automate and Chef Server
   - Implement proper variable handling and secrets management
   - Add idempotency checks

### Assumptions

1. The repository is primarily for educational/demonstration purposes rather than production use
2. The existing Ansible playbooks are functional but may not follow best practices
3. The Chef Automate deployment scripts are intended for initial setup only
4. The target environment is Ubuntu 20.04 as specified in kitchen.yml
5. Test Kitchen and InSpec are used for testing but may not be required in the final Ansible implementation
6. No complex Chef cookbooks or recipes need migration, only the deployment scripts
7. The migration goal is to standardize on Ansible rather than maintain a hybrid Chef/Ansible environment