# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components that demonstrate how Chef InSpec can be used alongside Ansible for compliance automation. The migration scope is relatively small, focusing on:

1. Chef InSpec test profiles that need to be preserved or migrated to Ansible-compatible testing frameworks
2. Chef Automate and Chef Infra Server deployment scripts that need to be replaced with Ansible equivalents
3. Existing Ansible playbooks that need to be reviewed and potentially refactored

The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited scope and the fact that some components are already in Ansible format.

## Module Migration Plan

This repository contains Chef and Ansible components that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Example showing Chef InSpec with Ansible for compliance automation
    - Path: chef-and-ansible
    - Technology: Mixed (Ansible playbooks with Chef InSpec tests)
    - Key Features: HTTPS website deployment, SSL configuration, InSpec compliance testing

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification. Migration consideration: Replace with Ansible-native testing framework like Molecule.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure website. Migration consideration: Review and potentially refactor to follow current Ansible best practices.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities. Migration consideration: Review and potentially refactor to follow current Ansible best practices.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website deployment. Migration consideration: Convert to Ansible-compatible test framework.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance. Migration consideration: Convert to Ansible-compatible test framework.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Migration consideration: Replace with Ansible playbook for infrastructure deployment.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Migration consideration: Replace with Ansible playbook for infrastructure deployment.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and apt package manager usage in playbooks)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver configuration)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's built-in `assert` module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static code analysis
  - Option 3: Use Molecule with Testinfra for more comprehensive testing
  - Option 4: Consider maintaining InSpec as a separate tool if its capabilities are required

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Tower/AWX for orchestration and job scheduling
  - GitLab CI/CD or GitHub Actions for pipeline automation
  - Compliance scanning tools like OpenSCAP or Ansible's built-in security automation

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for web servers. Ensure proper certificate management in the migrated Ansible solution.
  - Migration approach: Use Ansible's `openssl_*` modules as already demonstrated in the existing playbooks.

- **SSH Hardening**: The InSpec profile checks for SSH root login restrictions. Ensure these security checks are maintained.
  - Migration approach: Create Ansible roles for SSH hardening that apply the same security controls.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets detected in setup scripts (username/password in deploy-automate.sh and deploy-chef-server.sh)

### Technical Challenges

- **Compliance Testing**: The repository demonstrates using Chef InSpec for compliance testing with Ansible. Finding an equivalent solution in the Ansible ecosystem may be challenging.
  - Mitigation strategy: Evaluate Ansible's native assertion capabilities, Molecule with Testinfra, or maintain InSpec as a separate tool.

- **Chef Automate Replacement**: Chef Automate provides a comprehensive dashboard for compliance and infrastructure management.
  - Mitigation strategy: Implement a combination of Ansible Tower/AWX, compliance tools, and reporting solutions to replace Chef Automate's functionality.

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - Review and refactor `website_https.yml` and `poodle_fix.yml` to follow current Ansible best practices
   - Update any deprecated syntax or modules

2. **Testing Framework** (Moderate complexity)
   - Replace Test Kitchen with Molecule
   - Migrate InSpec tests to Ansible-compatible testing solutions

3. **Chef Deployment Scripts** (High complexity)
   - Create Ansible playbooks to replace the Chef Automate and Chef Infra Server deployment scripts
   - Implement secure credential management using Ansible Vault

### Assumptions

1. The primary purpose of this repository is for demonstration and educational purposes, not production deployment.
2. The InSpec tests are considered valuable and need to be preserved in some form.
3. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.
4. The deployment scripts for Chef Automate and Chef Infra Server need to be replaced with equivalent Ansible functionality.
5. No custom Chef cookbooks or recipes need to be migrated beyond what's visible in the repository.
6. The existing Ansible playbooks are functional and follow reasonable practices but may benefit from refactoring.
7. The security considerations in the InSpec profiles should be maintained in the migrated solution.