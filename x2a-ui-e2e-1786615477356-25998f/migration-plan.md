# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation and infrastructure configuration. The repository appears to be a demonstration or example repository showing how Chef InSpec can be used alongside Ansible for compliance testing. The migration scope is relatively small, focusing on:

1. Converting Chef InSpec tests to Ansible-compatible testing frameworks
2. Consolidating the existing Ansible playbooks into a more structured Ansible project
3. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks

Given the limited scope and small number of files, this migration is estimated to be low complexity and could be completed within 1-2 weeks by a single engineer familiar with both Chef and Ansible.

## Module Migration Plan

This repository contains a mix of Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook for deploying a secure Apache web server with HTTPS
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook for fixing SSL vulnerabilities in Apache (POODLE)
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **ssh_profile**:
    - Description: Chef InSpec test for SSH root login security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: Validates SSH configuration for root login restrictions

- **website_https_verify**:
    - Description: Chef InSpec test for HTTPS website validation
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Validates port 443 is listening, HTTPS status code, content verification, SSL protocol security

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework.
- `chef-and-ansible/index.html`: Simple HTML file used as a test page for the web server deployment.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role/playbook testing
  - Or continue using Test Kitchen with the Ansible provisioner (already in use)

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - Git repositories for playbook/role storage
  - Consider using Ansible Collections for organizing content

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Migration should maintain or improve the security posture:
  - Ensure TLSv1.2 or higher is enforced (currently done in poodle_fix.yml)
  - Consider adding more modern cipher suite configurations
  - Implement automatic certificate renewal if using Let's Encrypt

- **SSH Security**: The InSpec tests verify SSH root login is disabled. Migration should:
  - Maintain this security check in the new testing framework
  - Consider expanding SSH hardening in the Ansible playbooks

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates are generated on the fly, consider using Ansible Vault for pre-existing certificates

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach may require additional logic:
  - Challenge: InSpec's resource-based testing is more concise than Ansible's module-based approach
  - Mitigation: Create custom Ansible modules or use community modules that provide similar functionality

- **Test Kitchen Integration**: If keeping Test Kitchen:
  - Challenge: Ensuring the Ansible provisioner works correctly with the migrated playbooks
  - Mitigation: Update kitchen.yml to reflect new playbook structure and dependencies

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml):
   - Already in Ansible format, just need restructuring into roles
   - Low risk, high value as they form the core infrastructure code

2. **Chef Automate/Infra Server Deployment Scripts**:
   - Convert bash scripts to Ansible playbooks
   - Moderate complexity due to the need to handle Chef server installation and configuration

3. **InSpec Tests** (ssh_profile.rb, website_https_verify.rb):
   - Convert to Ansible-compatible testing framework
   - Higher complexity due to the different testing paradigms

### Assumptions

1. The repository is primarily for demonstration purposes and may not represent a production environment
2. The existing Ansible playbooks are functional and follow best practices
3. There are no external dependencies or integrations not visible in the repository
4. The target environment will continue to be Ubuntu 20.04 or similar
5. The migration will maintain the same level of security compliance testing
6. No additional features are required beyond what's currently implemented
7. The Chef InSpec tests are currently run as part of a CI/CD pipeline or manual testing process
8. The deployment scripts are used for setting up test environments rather than production systems