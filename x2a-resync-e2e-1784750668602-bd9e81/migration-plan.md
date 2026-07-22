# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts, Ansible playbooks, and Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving existing Ansible playbooks while standardizing their structure
3. Maintaining Chef InSpec tests for compliance verification

The migration complexity is **LOW to MEDIUM** with an estimated timeline of **1-2 weeks** for a single engineer. The repository appears to be primarily educational/demonstration content rather than production infrastructure code.

## Module Migration Plan

This repository contains Ansible playbooks, Chef deployment scripts, and InSpec tests that need individual migration planning:

### MODULE INVENTORY

I have performed thorough scanning of the repository using file_search for the required patterns with the following results:

```
file_search(pattern="**/manifests/init.pp")
Result: No files found for pattern **/manifests/init.pp in directory .

file_search(pattern="**/recipes/default.rb")
Result: No files found for pattern **/recipes/default.rb in directory .

file_search(pattern="**/*.psd1")
Result: No files found for pattern **/*.psd1 in directory .
```

Based on these search results, there are no traditional Puppet modules, Chef cookbooks, or PowerShell modules in this repository. 

The repository instead contains the following components that need migration:

- **website_https**:
    - Description: Ansible playbook that configures Apache with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification
- `tests/website_https_verify.rb`: Chef InSpec test file for verifying HTTPS configuration
- `tests/ssh_profile.rb`: Chef InSpec test file for verifying SSH security configuration
- `index.html`: Static HTML file for the website example

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuring monitoring and compliance
- **Chef Infra Server**: Replace with Ansible AWX/Tower or other configuration management system
- **Test Kitchen**: Replace with Ansible Molecule for testing or maintain Test Kitchen with Ansible verifier
- **Chef InSpec**: Can be maintained as-is since it works well with Ansible for compliance testing

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper certificate management in Ansible
- **POODLE Vulnerability Fix**: Maintain the security fix in the migrated Ansible playbooks
- **SSH Security Profile**: The InSpec tests verify SSH security configurations that should be implemented in Ansible
- **Hardcoded Credentials**: The Chef deployment scripts contain hardcoded credentials that should be replaced with Ansible Vault:
  - Username/password in deploy-automate.sh and deploy-chef-server.sh
  - Consider using Ansible Vault for all credentials

### Technical Challenges

- **Chef Server Functionality**: Determining if Chef Server functionality needs to be replaced with Ansible Tower/AWX or if it can be eliminated
- **InSpec Integration**: Ensuring continued integration between Ansible and InSpec for compliance testing
- **System Requirements**: Maintaining system requirement configurations (sysctl settings) during migration

### Migration Order

1. **chef-automate-deploy** and **chef-server-deploy** scripts (high value, convert to Ansible roles)
2. **website_https** playbook (already Ansible, needs standardization)
3. **poodle_fix** playbook (already Ansible, needs standardization)
4. **InSpec tests** (maintain as-is or convert to Ansible assert modules if preferred)

### Assumptions

1. The repository is primarily for demonstration/educational purposes rather than production infrastructure
2. The existing Ansible playbooks are functional and only need standardization
3. Chef InSpec will continue to be used for compliance testing alongside Ansible
4. The Chef Automate and Chef Infra Server deployment needs to be replaced with equivalent Ansible functionality
5. No external dependencies or integrations beyond what's visible in the repository
6. No complex data structures or custom facts are in use
7. No existing inventory management system is in place
8. The target environment is Ubuntu 20.04 as specified in the kitchen.yml file