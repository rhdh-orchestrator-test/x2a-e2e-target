# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation. The primary focus appears to be demonstrating how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are bash scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible components are already in place. The main migration tasks will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Replacing Chef Automate/Infra Server deployment scripts with Ansible playbooks
3. Ensuring all compliance checks are properly implemented in the new Ansible-only environment

Estimated timeline: 1-2 weeks for a small team (1-2 engineers)

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Collection of Ansible playbooks and Chef InSpec tests for compliance automation
    - Path: chef-and-ansible
    - Technology: Ansible/Chef InSpec
    - Key Features: Apache web server setup, SSL configuration, compliance testing

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server setup, user and organization management

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
- `chef-and-ansible/tests/website_https_verify.rb`: Chef InSpec test that verifies HTTPS functionality and security
- `chef-and-ansible/tests/ssh_profile.rb`: Chef InSpec control that ensures SSH root login is disabled
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/index.html`: Simple HTML file used as a test page for the web server
- `setup-automate/deploy-automate.sh`: Bash script to deploy Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Bash script to deploy Chef Infra Server without Automate

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM setup

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic compliance checks
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks

- **Test Kitchen**: Replace with Molecule for Ansible playbook testing
  - Molecule provides similar functionality but is more Ansible-native
  - Will require new configuration files but can reuse most test logic

- **Chef Automate/Infra Server**: Replace with Ansible alternatives:
  - AWX/Ansible Tower for web UI and job scheduling
  - Git repositories for playbook storage
  - CI/CD integration for automated testing and deployment

### Security Considerations

- **SSL Configuration**: The current implementation properly disables SSLv3 and enables only TLSv1.2, which should be maintained in the migrated solution
  - Migration approach: Keep the same SSL configuration logic in the Ansible playbooks

- **SSH Security**: The SSH root login check is critical and must be preserved
  - Migration approach: Convert the InSpec control to an Ansible task that checks the same configuration

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates are generated on the fly, which is acceptable for testing but should use proper certificate management for production

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require careful mapping of test assertions
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules
  - Consider using ansible.builtin.assert or ansible.builtin.fail modules for validation

- **Compliance Reporting**: InSpec provides rich compliance reporting that needs to be replicated
  - Mitigation: Integrate with AWX/Tower for reporting or use a dedicated compliance tool

- **Chef Server Functionality**: Some Chef Server functionality may need to be replicated in Ansible
  - Mitigation: Document which Chef Server features are actually being used and find Ansible equivalents

### Migration Order

1. **chef-and-ansible/website_https.yml** and **chef-and-ansible/poodle_fix.yml** (already in Ansible, no migration needed)
2. **chef-and-ansible/tests/website_https_verify.rb** (convert InSpec tests to Ansible tests)
3. **chef-and-ansible/tests/ssh_profile.rb** (convert InSpec control to Ansible task)
4. **setup-automate/deploy-automate.sh** and **setup-automate/deploy-chef-server.sh** (convert to Ansible roles for infrastructure setup)

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being a production deployment
2. The hardcoded credentials in the setup scripts are for demonstration purposes only
3. The self-signed certificates are acceptable for the intended use case
4. The target environment will continue to be Ubuntu 20.04 or compatible
5. There are no external dependencies or integrations not visible in the repository
6. The migration will maintain the same level of security compliance checking
7. Test Kitchen is only used for development/testing and not for production deployments