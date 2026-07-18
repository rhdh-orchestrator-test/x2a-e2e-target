# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single engineer, including testing and documentation.
**Complexity**: Low to Medium - The repository contains a limited number of files with clear purposes.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Integration of Chef InSpec with Ansible for compliance testing
    - Path: chef-and-ansible
    - Technology: Chef InSpec and Ansible
    - Key Features: HTTPS website deployment, SSL/TLS compliance testing, SSH security testing

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible and InSpec integration. Migration considerations include replacing with Ansible Molecule for testing.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure HTTPS website. Can be preserved as-is in the Ansible migration.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities. Can be preserved as-is in the Ansible migration.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for HTTPS website verification. Needs conversion to Ansible-compatible testing framework.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Needs conversion to Ansible-compatible testing framework.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate. Needs conversion to Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Needs conversion to Ansible playbook.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible Molecule for infrastructure testing
  - Option 2: ansible-test for module testing
  - Option 3: Integrate with pytest-ansible for more complex test scenarios

- **Test Kitchen**: Replace with Ansible Molecule for infrastructure testing and development workflow

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Tower/AWX for orchestration and control
  - Ansible Collections for configuration management
  - Ansible Content Hub for sharing Ansible content

### Security Considerations

- **SSL/TLS Configuration**: The repository includes SSL/TLS hardening (disabling SSLv3, enabling TLSv1.2). This security practice should be maintained in the Ansible migration.
  - Migration approach: Preserve the existing Ansible tasks in `poodle_fix.yml` and `website_https.yml` that handle SSL configuration.

- **SSH Security**: The repository includes SSH security testing (disabling root login). This security practice should be maintained in the Ansible migration.
  - Migration approach: Convert the InSpec test in `ssh_profile.rb` to an equivalent Ansible check using ansible-lint or Molecule.

- **Vault/secrets management**:
  - Hardcoded credentials in `deploy-automate.sh` and `deploy-chef-server.sh` (username, password, email)
  - Self-signed certificates in `website_https.yml`
  - Count: 2 credential sets detected (1 in each deployment script)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks may require learning new testing methodologies.
  - Mitigation: Use Ansible Molecule which provides a similar testing workflow to Test Kitchen.

- **Chef Automate Functionality**: Ensuring all Chef Automate functionality is properly replaced with Ansible Tower/AWX.
  - Mitigation: Carefully map Chef Automate features to Ansible Tower/AWX features and identify any gaps.

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - `website_https.yml`
   - `poodle_fix.yml`

2. **InSpec Tests** (Medium complexity)
   - Convert `website_https_verify.rb` to Ansible Molecule
   - Convert `ssh_profile.rb` to Ansible Molecule

3. **Chef Deployment Scripts** (High complexity)
   - Convert `deploy-chef-server.sh` to Ansible playbook
   - Convert `deploy-automate.sh` to Ansible playbook

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec integration with Ansible for compliance testing, not to provide production-ready infrastructure code.

2. The Chef Automate and Chef Infra Server deployment scripts are intended for demonstration or development environments, not production, given the hardcoded credentials.

3. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the code should be adaptable to other environments.

4. The migration goal is to eliminate Chef dependencies entirely, replacing them with Ansible-native solutions.

5. The existing Ansible playbooks (`website_https.yml` and `poodle_fix.yml`) are already well-structured and can be preserved with minimal changes.

6. Security testing is a primary concern, and equivalent security testing capabilities must be maintained in the Ansible migration.