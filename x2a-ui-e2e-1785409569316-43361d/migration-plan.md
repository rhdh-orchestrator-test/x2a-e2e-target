# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus is on using Chef InSpec for compliance testing alongside Ansible for configuration management. Additionally, there are bash scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate. The complexity is low to moderate, as the existing Ansible playbooks can be largely reused, while the InSpec tests need to be converted to Ansible-compatible testing frameworks like Molecule or ansible-test. The estimated timeline for migration is 1-2 weeks, with most of the effort focused on converting the InSpec tests to an Ansible-compatible testing framework.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing Test Kitchen with Molecule for Ansible testing.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality. Needs to be converted to Ansible-compatible testing framework.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for verifying SSH security configuration. Needs to be converted to Ansible-compatible testing framework.
- `chef-and-ansible/index.html`: Sample HTML file used for testing. Can be directly used in Ansible playbooks.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Test Kitchen (latest)**: Replace with Molecule for Ansible testing
- **InSpec (latest)**: Replace with Ansible-compatible testing frameworks:
  - For infrastructure testing: Molecule with testinfra or Ansible's assert module
  - For compliance testing: ansible-lint or OpenSCAP with Ansible integration

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper SSL protocols and ciphers are maintained during migration.
  - Migration approach: Preserve the SSL configuration in the Ansible playbooks, ensuring TLSv1.2 is enforced and older protocols are disabled.

- **SSH Security**: The InSpec tests verify SSH security configurations.
  - Migration approach: Create equivalent Ansible tasks to verify SSH configuration using assert module or testinfra.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password): Replace with Ansible Vault for secure credential storage.
  - Self-signed certificates: Maintain the same approach using Ansible's openssl modules, but consider using Ansible Vault for storing private keys.

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible-compatible testing frameworks.
  - Mitigation strategy: Use Molecule with testinfra for functional testing and ansible-lint for compliance checking. Map InSpec resources to equivalent testinfra or Ansible assert statements.

- **Chef Automate Deployment**: Replacing Chef Automate deployment scripts with Ansible playbooks.
  - Mitigation strategy: Create Ansible roles for deploying alternative compliance and infrastructure management tools like AWX/Ansible Tower or GitLab CI/CD with Ansible.

### Migration Order

1. **website_https.yml** (low risk, high value): Already an Ansible playbook, minimal changes needed
2. **poodle_fix.yml** (low risk, high value): Already an Ansible playbook, minimal changes needed
3. **InSpec Tests** (moderate complexity): Convert to Molecule with testinfra or Ansible assert module
4. **Chef Deployment Scripts** (high complexity): Create Ansible playbooks to deploy alternative tools

### Assumptions

1. The primary goal is to migrate all functionality to pure Ansible without relying on Chef components.
2. The InSpec tests need to be converted to an Ansible-compatible testing framework rather than maintained as InSpec tests.
3. The Chef Automate and Chef Infra Server deployment scripts need to be replaced with Ansible playbooks for deploying alternative tools.
4. The target environment will continue to be Ubuntu 20.04 running on Vagrant VMs.
5. The security requirements (SSL configuration, SSH security) need to be maintained in the migrated solution.
6. No external dependencies or integrations beyond what's visible in the repository need to be considered.
7. The migration will preserve the same functionality but using Ansible-native approaches where possible.