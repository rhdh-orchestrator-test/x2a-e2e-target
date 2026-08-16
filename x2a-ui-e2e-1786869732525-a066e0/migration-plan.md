# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec testing. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment shell scripts to Ansible playbooks
2. Preserving existing Ansible playbooks while standardizing their structure
3. Maintaining Chef InSpec tests as a compliance verification layer

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium - The repository contains a limited number of scripts and playbooks

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache with HTTPS, creates self-signed certificates, and deploys a simple website
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **chef-automate-deploy**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server with initial user and organization setup
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script that deploys Chef Infra Server (without Automate) with initial user and organization setup
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `tests/website_https_verify.rb`: InSpec test to verify HTTPS website deployment and SSL configuration
- `tests/ssh_profile.rb`: InSpec test to verify SSH security configuration (root login disabled)

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for deploying Chef Automate if still needed, or migrate to alternative solutions like AWX/Ansible Tower
- **Chef Server**: Replace with Ansible roles for configuration management or migrate to AWX/Ansible Tower
- **Test Kitchen**: Replace with Ansible Molecule for testing or maintain Test Kitchen with Ansible provisioner
- **InSpec**: Maintain as a compliance testing tool, which works well with Ansible

### Security Considerations

- **SSL/TLS Configuration**: The poodle_fix.yml playbook enforces TLSv1.2 and disables older protocols. This security hardening should be maintained in the migrated solution.
- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates. Consider enhancing with Let's Encrypt integration for production environments.
- **SSH Hardening**: The ssh_profile.rb InSpec test verifies that SSH root login is disabled. Ensure this security control is maintained.
- **Vault/secrets management**:
  - Hardcoded credentials in Chef deployment scripts (username, password) should be moved to Ansible Vault
  - Count: 2 scripts with hardcoded credentials (deploy-automate.sh, deploy-chef-server.sh)
  - Types: Username, password, email for Chef server admin user

### Technical Challenges

- **Chef Automate/Server Deployment**: Converting the Chef deployment scripts to Ansible will require understanding of Chef Automate/Server architecture and installation requirements. Ansible Galaxy may have existing roles that can be leveraged.
- **InSpec Integration**: Maintaining InSpec tests while migrating to pure Ansible requires understanding how to integrate InSpec with Ansible for compliance testing.
- **Test Kitchen to Molecule**: If migrating testing framework, there will be a learning curve for teams familiar with Test Kitchen but not Molecule.

### Migration Order

1. **Existing Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format, just need standardization
2. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Medium complexity, requires converting bash scripts to Ansible playbooks
3. **Testing Framework**: Optional migration from Test Kitchen to Molecule if desired

### Assumptions

1. The repository is primarily used for examples and demonstrations rather than production deployments
2. The InSpec tests are intended to be maintained as a compliance verification layer
3. The hardcoded credentials in the Chef deployment scripts are for demonstration purposes only
4. The target environment is Ubuntu 20.04 as specified in the kitchen.yml file
5. The Apache configuration in the Ansible playbooks is for demonstration purposes and may need enhancement for production use
6. The self-signed certificates are acceptable for the demonstration environment but would need to be replaced with proper certificates in production
7. The repository does not contain actual Chef cookbooks or recipes that need migration, only deployment scripts for Chef infrastructure