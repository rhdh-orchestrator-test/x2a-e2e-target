# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus is on using Chef InSpec for compliance testing alongside Ansible for configuration management. The repository also includes Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity as most components are already in Ansible format.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate the POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **inspec_tests**:
    - Description: Chef InSpec tests for verifying HTTPS website functionality and SSH security compliance
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: HTTPS verification, SSL protocol testing, SSH configuration compliance checks

- **chef_deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash scripts using Chef CLI tools
    - Key Features: Chef Automate deployment, Chef Infra Server configuration, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible Molecule for testing.
- `index.html`: Sample HTML file used for testing the web server. Can be directly used in Ansible content.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible alternatives:
  - For compliance testing: Use Ansible's built-in assert module or migrate to ansible-lint
  - For infrastructure testing: Use Molecule with Testinfra or Goss
  - For security compliance: Consider OpenSCAP with Ansible integration

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure code

- **Chef Automate/Infra Server**: Consider migrating to:
  - Ansible Tower/AWX for orchestration and management
  - Ansible Content Collections for role and playbook management
  - GitLab CI/CD or GitHub Actions for pipeline automation

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Migration should maintain or improve the security posture:
  - Ensure TLS 1.2+ is enforced (as in the current poodle_fix.yml)
  - Consider using Let's Encrypt instead of self-signed certificates
  - Implement modern cipher suites

- **SSH Hardening**: The InSpec tests verify SSH root login is disabled. Ensure this security check is maintained in the Ansible migration.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely
  - Count of credentials detected: 3 (username, password, and SSL certificates)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible verification methods will require careful mapping of test assertions.
  - Mitigation: Use Ansible's assert module or consider integrating with Molecule and Testinfra for similar functionality.

- **Chef Automate Functionality**: If the team relies on Chef Automate features, equivalent functionality must be identified in Ansible Tower/AWX.
  - Mitigation: Conduct a feature comparison and plan for any gaps in functionality.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format, may only need style adjustments or best practice updates.
2. **InSpec Tests**: Moderate complexity to convert to Ansible-compatible testing frameworks.
3. **Chef Deployment Scripts**: Higher complexity, requires replacing Chef Automate/Infra Server with Ansible Tower/AWX or similar solution.

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production, based on the README description.
2. The InSpec tests are used for compliance verification of configurations managed by Ansible.
3. The Chef Automate and Chef Infra Server deployment scripts are separate from the main Ansible+InSpec workflow.
4. The target environment is Ubuntu 20.04 running on Vagrant VMs.
5. There are no external dependencies or integrations beyond what's visible in the repository.
6. The hardcoded credentials in the deployment scripts are for demonstration purposes only.
7. The migration will maintain the same level of security compliance testing.
8. No custom Chef resources or complex Chef-specific functionality is being used that would require special handling.