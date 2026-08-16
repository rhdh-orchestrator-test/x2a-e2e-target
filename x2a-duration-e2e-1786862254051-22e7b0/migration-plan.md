# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks designed to demonstrate compliance automation with Chef InSpec alongside Ansible. The repository also includes Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium - The repository primarily contains Ansible playbooks that won't need significant changes, with the main effort focused on migrating Chef InSpec tests to an Ansible-compatible testing framework.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS configuration and self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2 in Apache configuration

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS configuration on the web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Tests port 443 listening, HTTPS response, SSL/TLS protocol security

- **ssh_profile**:
    - Description: Chef InSpec profile that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: Checks SSH root login is disabled, implements STIG compliance checks

- **automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Configures system settings, downloads and deploys Chef Automate, creates initial user and organization

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Configures system settings, downloads and deploys Chef Infra Server, creates initial user and organization

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be updated to use Ansible-native testing frameworks.
- `index.html`: Simple HTML file used for testing the web server deployment.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Molecule with Testinfra for infrastructure testing
  - Option 2: Ansible Test for compliance testing
  - Option 3: Convert InSpec tests to Ansible assert tasks

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role and playbook testing
  - Ansible Test for module testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Automation Platform for enterprise automation
  - AWX (open-source version of Ansible Tower) for smaller deployments
  - GitLab CI/CD or Jenkins for pipeline orchestration

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable insecure protocols. This security hardening should be preserved in the migrated Ansible playbooks.
  
- **Self-signed Certificates**: The playbooks generate self-signed certificates. Consider enhancing with Let's Encrypt integration for production environments.

- **SSH Hardening**: The InSpec profile checks for SSH root login restrictions. This should be implemented as an Ansible task and verified with Ansible-compatible tests.

- **Vault/secrets management**: 
  - Hardcoded credentials in the deployment scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deployment scripts

### Technical Challenges

- **Test Framework Migration**: Converting Chef InSpec tests to Ansible-compatible testing frameworks will require understanding the test assertions and recreating them in the new framework.
  - Mitigation: Use Molecule with Testinfra which has similar syntax to InSpec, or convert tests to Ansible assert tasks.

- **Compliance Testing**: The repository includes STIG compliance checks in InSpec. These will need to be recreated in the Ansible ecosystem.
  - Mitigation: Use DISA STIG Ansible roles from the community or convert the InSpec controls to Ansible tasks with assert statements.

- **Chef Automate Replacement**: Finding an equivalent to Chef Automate's compliance reporting in the Ansible ecosystem.
  - Mitigation: Implement Ansible Automation Platform with compliance scanning or integrate with a third-party compliance tool.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already Ansible and only need minor updates to follow best practices.
   
2. **Testing Framework**: Convert InSpec tests to Molecule/Testinfra or Ansible assert tasks.
   
3. **Deployment Scripts**: Convert Chef Automate and Chef Infra Server deployment scripts to Ansible roles/playbooks.

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production, as indicated by the README mentioning it's related to content created by Technical Product Marketing.

2. The Chef InSpec tests are used for compliance validation of infrastructure configured by Ansible, not for validating Chef-managed infrastructure.

3. The deployment scripts are used for setting up test environments and not production Chef infrastructure.

4. The hardcoded credentials in the deployment scripts are for demonstration purposes and not used in production environments.

5. The target environment is Ubuntu 20.04 as specified in the kitchen.yml file.

6. The migration will preserve the existing functionality while moving away from Chef components.

7. No external dependencies or integrations beyond what's visible in the repository need to be considered.