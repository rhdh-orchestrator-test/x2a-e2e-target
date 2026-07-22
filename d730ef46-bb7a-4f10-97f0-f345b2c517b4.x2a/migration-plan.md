# MIGRATION FROM CHEF/BASH TO ANSIBLE

## Executive Summary

This repository contains a mix of Bash scripts for Chef Automate/Chef Server deployment and Ansible playbooks with Chef InSpec tests. The repository appears to be primarily focused on demonstrating how Chef InSpec can be used alongside Ansible for compliance automation, rather than containing a full production infrastructure codebase.

After thorough examination using file_search for Chef cookbooks (`**/recipes/default.rb`), Puppet modules (`**/manifests/init.pp`), and PowerShell modules (`**/*.psd1`), no traditional infrastructure-as-code modules were found. The repository consists of Ansible playbooks and Bash deployment scripts.

The migration scope is relatively small, focusing on converting the Chef Automate and Chef Server deployment Bash scripts to Ansible playbooks. The estimated timeline for this migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains the following technologies that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
I have verified using `file_search` that there are no traditional Chef cookbooks (`**/recipes/default.rb`), Puppet modules (`**/manifests/init.pp`), or PowerShell modules (`**/*.psd1`) in this repository.

The repository contains:

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts
    - Key Features: Automated deployment of Chef Automate and Chef Infra Server, user and organization creation

- **website-https**:
    - Description: Ansible playbook for deploying a secure website with Apache and SSL
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook for fixing SSL vulnerabilities in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **inspec-compliance-tests**:
    - Description: Chef InSpec tests for verifying security compliance
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: SSH security verification, HTTPS website verification

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with Vagrant
- `chef-and-ansible/tests/website_https_verify.rb`: Chef InSpec tests for verifying the HTTPS website deployment
- `chef-and-ansible/tests/ssh_profile.rb`: Chef InSpec tests for verifying SSH security compliance
- `chef-and-ansible/index.html`: Sample HTML file for website testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in Test Kitchen configuration)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for deploying Chef Automate and Chef Infra Server, or consider if these components are still needed
- **Test Kitchen with Vagrant**: Replace with Ansible Molecule for testing Ansible roles and playbooks
- **Chef InSpec**: Can be retained as a testing framework or replaced with Ansible's built-in assert module and other testing tools

### Security Considerations

- **SSL Configuration**: The playbooks include SSL hardening (disabling SSLv3, enabling TLSv1.2) which should be preserved in the migrated code
- **Self-signed Certificates**: The current implementation uses self-signed certificates; consider using Let's Encrypt for production environments
- **SSH Security**: The InSpec tests verify SSH security configurations that should be maintained in the Ansible implementation
- **Vault/secrets management**: 
  - Hardcoded credentials in the deployment scripts (username, password) should be moved to Ansible Vault
  - Count: 2 sets of credentials in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **Chef Automate Deployment**: Converting the Chef Automate and Chef Infra Server deployment scripts to Ansible may require additional research on the deployment process and requirements
- **InSpec Integration**: Ensuring that the InSpec tests continue to work with the Ansible-managed infrastructure
- **Compliance Testing**: Determining whether to keep Chef InSpec for compliance testing or migrate to an Ansible-native solution

### Migration Order

1. Create Ansible roles for Chef Automate and Chef Infra Server deployment (high value, moderate complexity)
2. Update Test Kitchen configuration to use Molecule for testing (low risk)
3. Enhance security by implementing Ansible Vault for credentials (moderate complexity)
4. Evaluate whether to keep Chef InSpec for compliance testing or migrate to Ansible-native solutions (low risk, high value)

### Assumptions

1. The repository is primarily for demonstration purposes and not a production infrastructure codebase
2. The Chef InSpec tests are intended to be used alongside Ansible for compliance testing
3. The hardcoded credentials in the deployment scripts are for demonstration purposes only
4. The target environment is Ubuntu 20.04 running on Vagrant VMs
5. The migration goal is to have a fully Ansible-managed infrastructure while retaining the compliance testing capabilities