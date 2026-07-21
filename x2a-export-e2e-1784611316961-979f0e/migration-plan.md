# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec testing. After thorough examination using file_search for patterns like "**/manifests/init.pp", "**/recipes/default.rb", and "**/*.psd1", no traditional Puppet modules, Chef cookbooks, or PowerShell modules were found. The repository primarily consists of Ansible playbooks and bash scripts for Chef server deployment.

The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving and enhancing the existing Ansible playbooks
3. Maintaining the Chef InSpec testing capabilities within the Ansible framework

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers), given the limited scope and complexity.

## Module Migration Plan

This repository contains a mix of technologies that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
File searches were performed for the following patterns to identify modules:
- `file_search(pattern="**/manifests/init.pp")` - Result: "No files found for pattern **/manifests/init.pp in directory ." (no Puppet modules)
- `file_search(pattern="**/recipes/default.rb")` - Result: "No files found for pattern **/recipes/default.rb in directory ." (no Chef cookbooks)
- `file_search(pattern="**/*.psd1")` - Result: "No files found for pattern **/*.psd1 in directory ." (no PowerShell modules)
- `file_search(pattern="**/*.rb")` - Result: "No files found for pattern **/*.rb in directory ." (no Ruby files in main directories)
- `file_search(pattern="chef-and-ansible/**/*.rb")` - Result: "No files found for pattern chef-and-ansible/**/*.rb in directory ." (no Ruby files in chef-and-ansible)
- `list_directory(dir_path="chef-and-ansible/tests")` - Result: "ssh_profile.rb, website_https_verify.rb" (InSpec test files only)

Based on these verified searches, no traditional infrastructure-as-code modules were found. The repository contains:

- **chef-and-ansible**:
    - Description: Ansible playbooks for deploying a secure Apache web server with HTTPS, with Chef InSpec tests for validation
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec testing
    - Key Features: SSL/TLS configuration, Apache virtual host setup, compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts with Chef server deployment
    - Key Features: Chef Automate deployment, Chef Infra Server setup, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying Apache with HTTPS
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec tests for validating HTTPS configuration
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec tests for SSH security compliance
- `setup-automate/deploy-automate.sh`: Bash script to deploy Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Bash script to deploy only Chef Infra Server

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Maintain InSpec for compliance testing, integrate with Ansible using the `ansible.builtin.shell` module or migrate to Ansible's built-in assertion modules
- **Test Kitchen**: Replace with Ansible Molecule for testing Ansible roles and playbooks
- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that achieve the same server setup

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable insecure protocols (SSL3). This security hardening must be preserved in the migrated Ansible playbooks.
- **SSH Hardening**: InSpec tests verify SSH root login is disabled. Ensure the migrated solution maintains this security check.
- **Credentials Management**: 
  - Hardcoded credentials in `setup-automate` scripts (username, password, email)
  - These should be moved to Ansible Vault or another secure secrets management solution
  - Count: 5 credential-related variables in each deployment script

### Technical Challenges

- **InSpec Integration**: Determining the best approach to integrate Chef InSpec tests with pure Ansible deployments:
  - Option 1: Use Ansible's `community.general.inspec` module to run InSpec tests
  - Option 2: Use Ansible's built-in assertion capabilities to replace InSpec tests
  - Option 3: Maintain InSpec as a separate tool called via Ansible's shell module

- **Chef Server Deployment**: Converting the Chef server deployment scripts to idempotent Ansible playbooks:
  - Challenge: Ensuring proper error handling and idempotence for server setup
  - Mitigation: Use Ansible's built-in modules for package management, service control, and file operations with appropriate state checking

### Migration Order

1. **chef-and-ansible Playbooks** (low risk, already Ansible)
   - Refactor existing Ansible playbooks to follow best practices
   - Update Test Kitchen configuration to use Molecule instead

2. **InSpec Tests** (moderate complexity)
   - Decide on integration approach
   - Adapt or convert tests to work with the new Ansible-only workflow

3. **Chef Server Deployment Scripts** (high complexity)
   - Convert bash scripts to Ansible playbooks
   - Implement secure credential management
   - Test deployment process thoroughly

### Assumptions

1. The repository is primarily used for demonstration/example purposes rather than production deployments (based on README content)
2. The Chef InSpec tests are valuable and should be preserved rather than replaced
3. The hardcoded credentials in deployment scripts are for demonstration only and would be replaced in actual deployments
4. The target environment for the migrated solution will continue to be Ubuntu 20.04 or compatible systems
5. The Apache configuration requirements (SSL/TLS settings, virtual hosts) will remain the same in the migrated solution