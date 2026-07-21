# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec testing. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment shell scripts to Ansible playbooks
2. Preserving and enhancing existing Ansible playbooks
3. Maintaining the InSpec testing capabilities within an Ansible-only workflow

The migration complexity is **LOW** with an estimated timeline of 1-2 weeks, as most of the repository already uses Ansible with InSpec for testing. The primary work involves converting the Chef server deployment scripts to Ansible playbooks and ensuring the InSpec tests continue to function properly in the new workflow.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
I have verified that there are no Puppet modules (no files matching **/manifests/init.pp), no Chef cookbooks (no files matching **/recipes/default.rb), and no PowerShell modules (no files matching **/*.psd1) in this repository.

The repository contains Ansible playbooks and bash scripts for Chef server deployment:

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **chef-automate-deploy**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server on a VM
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script that deploys Chef Infra Server (without Automate) on a VM
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be updated to use Ansible-only testing framework.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test file that verifies the HTTPS website configuration. Can be preserved as-is for compliance testing.
- `chef-and-ansible/index.html`: Likely a sample file for testing web server configuration.
- `README.md`: Repository documentation files.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Maintain as a compliance testing tool within the Ansible workflow
- **Test Kitchen**: Replace with Ansible Molecule for testing or adapt to use only Ansible
- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks

### Security Considerations

- **SSL Configuration**: The poodle_fix.yml playbook enforces TLSv1.2 and disables older protocols. This security hardening should be preserved in the migrated solution.
- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates. Consider enhancing with Let's Encrypt integration.
- **Vault/secrets management**: 
  - Hardcoded credentials in setup-automate scripts (username, password)
  - No encryption or vault usage detected in the current implementation
  - Migration should implement Ansible Vault for credential storage

### Technical Challenges

- **InSpec Integration**: Ensuring Chef InSpec tests continue to work seamlessly with Ansible-only workflows
- **Chef Server Deployment**: Converting the Chef server deployment scripts to idempotent Ansible playbooks
- **Testing Framework**: Replacing Test Kitchen with an Ansible-native testing solution like Molecule

### Migration Order

1. **website_https and poodle_fix playbooks** (low risk, already Ansible)
   - Review and optimize existing Ansible playbooks
   - Update to use Ansible best practices (roles, variables, etc.)
   - Implement Ansible Vault for any sensitive data

2. **Testing Framework** (moderate complexity)
   - Migrate from Test Kitchen to Ansible Molecule or similar
   - Ensure InSpec tests continue to function properly

3. **Chef Server Deployment Scripts** (high complexity)
   - Convert bash scripts to Ansible playbooks
   - Implement idempotency checks
   - Use Ansible Vault for credentials

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than to provide production-ready infrastructure code.
2. The Chef Automate and Chef Infra Server deployment scripts are intended for demonstration or development environments, given the hardcoded credentials.
3. The target environment will continue to be Ubuntu 20.04 or compatible systems.
4. InSpec will remain the preferred testing/compliance tool even after migration to Ansible.
5. No external dependencies or integrations beyond what's visible in the repository.