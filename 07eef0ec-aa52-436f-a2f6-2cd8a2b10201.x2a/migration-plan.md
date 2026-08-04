# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate deployment scripts and Ansible playbooks that are used for demonstration and educational purposes. The repository appears to be focused on showing how Chef InSpec can be used alongside Ansible for compliance automation, rather than being a production infrastructure codebase.

The migration scope is relatively small, with only a few deployment scripts and Ansible playbooks to consider. The estimated timeline for migration would be 1-2 days given the limited scope and straightforward nature of the code.

## Module Migration Plan

This repository contains the following technologies that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate the POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart

- **chef-automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks in a Vagrant environment
- `tests/website_https_verify.rb`: Chef InSpec test file to verify the HTTPS website deployment
- `index.html`: Simple HTML file used for testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server**: Replace with Ansible AWX/Tower or other Ansible-based configuration management
- **Chef InSpec**: Can be retained for compliance testing with Ansible, as this is already the demonstrated use case

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache with self-signed certificates. Migration should maintain or improve this security practice.
- **POODLE Vulnerability Mitigation**: The poodle_fix.yml playbook specifically addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2. This security practice should be maintained.
- **Vault/secrets management**:
  - Hardcoded credentials in the deployment scripts (username, password, email)
  - Self-signed SSL certificates generated during deployment
  - No formal secrets management is implemented in the current code

### Technical Challenges

- **Chef Automate Deployment**: The bash scripts for deploying Chef Automate and Chef Server would need to be replaced with Ansible roles that accomplish the same configuration. This may require research into the Chef Automate API or installation process.
- **InSpec Integration**: The current setup uses InSpec for compliance testing with Ansible. This integration should be preserved or enhanced in the migration.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): These are already in Ansible format and only need review and potential optimization.
2. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Convert these bash scripts to Ansible roles for deploying configuration management tools.

### Assumptions

1. The repository is primarily for demonstration purposes and not a production infrastructure codebase.
2. The main goal is to show how Chef InSpec can be used with Ansible for compliance automation.
3. The hardcoded credentials in the deployment scripts are for demonstration purposes only.
4. The target environment is Ubuntu 20.04 running in Vagrant VMs.
5. The migration is focused on standardizing on Ansible rather than maintaining a hybrid Chef/Ansible environment.
6. The InSpec tests should be preserved as they demonstrate the compliance automation aspect.