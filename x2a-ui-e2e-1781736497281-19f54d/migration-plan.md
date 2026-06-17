# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mixed environment of Chef and Ansible components focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, with two main components:

1. A demonstration environment showing Chef InSpec with Ansible playbooks
2. Chef Automate/Chef Server deployment scripts

The migration complexity is **LOW** as most of the content is already in Ansible format, with the primary focus being on replacing Chef InSpec with an Ansible-native compliance solution. Estimated timeline: **1-2 weeks**.

## Module Migration Plan

This repository contains Chef and Ansible components that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Demonstration of Chef InSpec for compliance testing with Ansible playbooks
    - Path: chef-and-ansible/
    - Technology: Mixed (Ansible playbooks with Chef InSpec tests)
    - Key Features: HTTPS website deployment, SSL configuration, compliance testing

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash scripts for Chef infrastructure deployment
    - Key Features: Chef Automate deployment, Chef Server deployment, user/organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration consideration: Replace with Ansible Molecule for testing.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying HTTPS website. Migration consideration: Already in Ansible format, can be used as-is.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability. Migration consideration: Already in Ansible format, can be used as-is.
- `chef-and-ansible/tests/website_https_verify.rb`: Chef InSpec test for HTTPS website. Migration consideration: Convert to Ansible-native testing solution.
- `chef-and-ansible/tests/ssh_profile.rb`: Chef InSpec profile for SSH compliance. Migration consideration: Convert to Ansible-native testing solution.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Migration consideration: Replace with Ansible playbook for infrastructure deployment.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Migration consideration: Replace with Ansible playbook for infrastructure deployment.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and package versions in Ansible playbooks)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver configuration)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native compliance solutions:
  - Option 1: Ansible's built-in `assert` module for basic compliance checks
  - Option 2: Ansible Lint for static code analysis
  - Option 3: Ansible's integration with OpenSCAP for compliance scanning
  - Option 4: Continue using InSpec but invoke it from Ansible

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Server**: Replace deployment scripts with Ansible playbooks that either:
  - Option 1: Deploy alternative compliance and infrastructure management tools
  - Option 2: Continue to deploy Chef components but using Ansible for the deployment process

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper certificate management in the migrated solution.
  - Migration approach: Use Ansible's `openssl_*` modules as already demonstrated in the existing playbooks.

- **SSH Hardening**: The InSpec profile checks for SSH root login disablement.
  - Migration approach: Implement equivalent checks using Ansible's assert module or OpenSCAP integration.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets identified in the setup scripts

### Technical Challenges

- **Compliance Testing**: The primary challenge is replacing Chef InSpec with an equivalent Ansible-native solution.
  - Mitigation strategy: Evaluate Ansible's built-in assertion capabilities, OpenSCAP integration, or continue using InSpec called from Ansible.

- **Infrastructure Deployment**: The Chef Automate/Server deployment scripts need to be converted to Ansible playbooks.
  - Mitigation strategy: Create equivalent Ansible roles for infrastructure deployment, potentially leveraging community roles if available.

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - `website_https.yml` and `poodle_fix.yml` can be used as-is
   - Update testing framework from Test Kitchen to Molecule

2. **Compliance Testing** (Moderate complexity)
   - Convert InSpec tests to Ansible-native testing solutions
   - Implement equivalent compliance checks for SSH and HTTPS

3. **Infrastructure Deployment Scripts** (Higher complexity)
   - Convert Chef Automate/Server deployment bash scripts to Ansible playbooks
   - Implement proper secret management with Ansible Vault

### Assumptions

1. The primary goal is to standardize on Ansible and eliminate Chef dependencies where possible.
2. The InSpec tests are valuable and equivalent functionality should be preserved in the Ansible migration.
3. The deployment scripts are used for setting up test/demo environments rather than production systems.
4. No actual Chef cookbooks or recipes need migration as none were identified in the repository.
5. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with proper secret management in production.
6. The target environment will continue to be Ubuntu 20.04 or compatible systems.
7. The team has experience with Ansible but may need guidance on compliance testing approaches in Ansible.