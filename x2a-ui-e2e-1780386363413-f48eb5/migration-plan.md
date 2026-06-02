# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

Estimated timeline: 1-2 weeks for a single developer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate the POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2 in Apache configuration

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration verification, security compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible-native testing framework like Molecule.
- `index.html`: Simple HTML file used for testing. Migration consideration: Keep as-is or include as a template in Ansible.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be environment-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Use Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing
  - Option 4: Keep InSpec but run it from Ansible using the `command` module

- **Test Kitchen**: Replace with Molecule for testing Ansible roles and playbooks

- **Chef Automate/Infra Server**: Replace with appropriate Ansible automation platform:
  - Option 1: Ansible Automation Platform (Red Hat)
  - Option 2: AWX (open-source version of Ansible Tower)
  - Option 3: Simple GitLab CI/CD or Jenkins pipeline for Ansible playbook execution

### Security Considerations

- **SSL Configuration**: The `poodle_fix.yml` playbook addresses the POODLE vulnerability by enforcing TLSv1.2. This security configuration should be preserved in the migrated solution.
  
- **SSH Security**: The `ssh_profile.rb` InSpec test verifies that SSH root login is disabled. This security check should be migrated to an equivalent Ansible-based test.

- **Self-signed Certificates**: The `website_https.yml` playbook generates self-signed certificates. Consider enhancing security by using Let's Encrypt certificates in the migrated solution.

- **Vault/secrets management**: 
  - Hardcoded credentials in `deploy-automate.sh` and `deploy-chef-server.sh` (username, password) should be moved to Ansible Vault
  - Count of credentials detected: 2 sets of credentials in deployment scripts

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks may require learning new testing methodologies and syntax.
  - Mitigation: Use Ansible's built-in modules like `uri`, `stat`, and `assert` to replicate InSpec tests, or consider using Ansible Lint and Molecule for more comprehensive testing.

- **Chef Automate Functionality**: Replacing Chef Automate's functionality with Ansible equivalents requires understanding the specific features being used.
  - Mitigation: Evaluate which Chef Automate features are actually being used and find appropriate Ansible alternatives (e.g., AWX/Tower for web UI, GitLab/Jenkins for CI/CD).

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): These are already in Ansible format and require minimal changes, mainly to improve structure and follow best practices.

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert these to Ansible-compatible testing frameworks.

3. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Convert these to Ansible playbooks for infrastructure deployment.

4. **Infrastructure Files** (kitchen.yml): Replace with Molecule configuration for testing.

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, as indicated in the README.md.

2. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are working correctly and don't need functional changes, just structural improvements.

3. There's no complex Chef cookbook logic that needs to be migrated, as the repository focuses on InSpec tests rather than Chef recipes.

4. The deployment scripts (deploy-automate.sh, deploy-chef-server.sh) are used for setting up a test environment rather than production infrastructure.

5. The target environment is Ubuntu 20.04 running on Vagrant VMs, as specified in kitchen.yml.

6. The security compliance requirements (SSH configuration, SSL protocols) are important and must be preserved in the migrated solution.

7. There are no external dependencies or integrations beyond what's visible in the repository.