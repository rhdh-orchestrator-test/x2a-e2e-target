# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on two main components:

1. Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks
2. Existing Ansible playbooks with InSpec tests that need to be standardized and integrated into a unified Ansible framework

The migration complexity is **LOW to MEDIUM** with an estimated timeline of **1-2 weeks** for a single engineer, as the codebase is small and well-structured. The main challenge will be preserving the Chef InSpec testing functionality while moving away from the Chef server infrastructure.

## Module Migration Plan

This repository contains both Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
I have verified that no traditional Chef cookbooks (with recipes/default.rb), Puppet modules (with manifests/init.pp), or PowerShell modules (.psd1) exist in this repository. The following searches confirmed this:
- `file_search(pattern="**/manifests/init.pp")` - No results
- `file_search(pattern="**/recipes/default.rb")` - No results
- `file_search(pattern="**/*.psd1")` - No results

The repository instead contains Ansible playbooks and bash scripts that need migration:

- **website-https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration, including self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **chef-automate-deploy**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `tests/website_https_verify.rb`: InSpec test for verifying HTTPS website deployment
- `tests/ssh_profile.rb`: InSpec test for verifying SSH security configuration
- `chef-and-ansible/index.html`: Static HTML file for the website

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Currently used for compliance testing. Replace with:
  - Ansible's built-in `assert` module for basic tests
  - Molecule for more comprehensive testing
  - Consider maintaining InSpec tests but running them via Ansible rather than Chef

- **Test Kitchen**: Currently used for test orchestration. Replace with:
  - Molecule for Ansible role testing
  - Ansible Playbook testing with Molecule

- **Chef Automate/Infra Server**: Currently deployed via bash scripts. Replace with:
  - Ansible playbooks that configure equivalent monitoring and compliance solutions
  - Consider migrating to AWX/Ansible Tower for web UI and automation capabilities

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with SSL/TLS. Migration should:
  - Maintain or improve the security of the SSL configuration
  - Update the SSL protocol settings to current best practices
  - Use Ansible Vault for storing certificate information

- **SSH Hardening**: The repository includes InSpec tests for SSH security. Migration should:
  - Implement equivalent SSH hardening in Ansible
  - Maintain compliance with the security requirements in the InSpec tests

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Self-signed certificates generated in the website_https.yml playbook
  - Migration should use Ansible Vault to secure these credentials

### Technical Challenges

- **InSpec Test Integration**: Preserving the compliance testing functionality while moving away from Chef
  - Mitigation: Use Ansible's assert module for basic tests, or maintain InSpec and call it from Ansible

- **Certificate Management**: The current solution generates self-signed certificates
  - Mitigation: Use Ansible's crypto modules for certificate generation or integrate with Let's Encrypt

- **Configuration Validation**: Ensuring the migrated Ansible playbooks produce identical system states
  - Mitigation: Use the existing InSpec tests to validate the migrated playbooks

### Migration Order

1. **website-https playbook** (low risk, already in Ansible)
   - Standardize according to Ansible best practices
   - Add documentation and improve variable usage

2. **poodle-fix playbook** (low risk, already in Ansible)
   - Standardize according to Ansible best practices
   - Consider merging with website-https as a role

3. **InSpec Tests** (medium risk)
   - Convert to Ansible assertions or maintain as InSpec but called from Ansible

4. **Chef Deployment Scripts** (high complexity)
   - Create Ansible playbooks to replace Chef Automate/Infra Server deployment
   - Consider alternative solutions like AWX/Ansible Tower

### Assumptions

1. The primary goal is to eliminate Chef dependencies while maintaining the same functionality
2. The InSpec tests are valuable and should be preserved in some form
3. The deployment scripts for Chef Automate/Infra Server need to be replaced with equivalent Ansible functionality
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. The self-signed certificates are acceptable for the environment (not production)
6. The hardcoded credentials in the deployment scripts are for demonstration purposes only
7. Test Kitchen can be replaced with Molecule or another Ansible-native testing framework