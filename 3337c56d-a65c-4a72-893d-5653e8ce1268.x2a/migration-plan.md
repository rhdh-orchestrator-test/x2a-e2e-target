# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on infrastructure automation and compliance testing. The primary migration scope involves:

1. Chef Automate and Chef Infra Server deployment scripts
2. Chef InSpec compliance tests used alongside Ansible playbooks
3. Integration of Test Kitchen with Ansible and InSpec

The migration complexity is **LOW to MEDIUM** as the repository already contains Ansible playbooks and primarily uses Chef for compliance testing via InSpec. The estimated timeline for migration is **2-3 weeks**, focusing on replacing Chef InSpec with Ansible-native solutions like ansible-lint and integrating with other compliance tools.

## Module Migration Plan

This repository contains Chef and Ansible components that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Integration of Chef InSpec with Ansible for compliance automation
    - Path: chef-and-ansible
    - Technology: Mixed (Ansible playbooks with Chef InSpec tests)
    - Key Features: HTTPS website deployment, SSL configuration, compliance testing

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration should replace with Ansible-native testing framework like Molecule.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying HTTPS website. Can be kept as-is or refactored to use Ansible collections.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for SSL security fixes. Can be kept as-is or refactored to use Ansible collections.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for HTTPS website verification. Should be migrated to Ansible-native testing.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec compliance profile for SSH security. Should be migrated to Ansible-native compliance testing.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Should be replaced with Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Should be replaced with Ansible playbook.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and package versions in Ansible playbooks)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with ansible-lint for basic linting and one of the following for compliance testing:
  - OpenSCAP with ansible-openscap
  - Ansible Compliance as Code framework
  - Ansible integration with Compliance as Code tools like OSCAP Ansible

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that can:
  - Set up equivalent monitoring and compliance infrastructure
  - Configure user management and organization structure
  - Implement similar automation workflows

### Security Considerations

- **SSL Configuration**: The `poodle_fix.yml` playbook addresses SSL vulnerabilities by enforcing TLSv1.2. This security practice should be maintained in the migrated solution.
  
- **SSH Security**: The `ssh_profile.rb` InSpec test enforces SSH root login restrictions. This should be migrated to an equivalent Ansible check or integrated with ansible-lint security checks.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - SSL certificate generation in `website_https.yml` should use Ansible Vault for key storage
  - Total credentials detected: 3 (username, password, SSL keys)

### Technical Challenges

- **Compliance Testing**: Replacing InSpec with Ansible-native compliance testing may require additional tooling or custom development. Mitigation: Evaluate ansible-lint, OpenSCAP integration, and other compliance frameworks compatible with Ansible.

- **Test Framework**: Migrating from Test Kitchen to Molecule will require reconfiguration of test scenarios. Mitigation: Create equivalent Molecule scenarios that test the same functionality.

- **Chef Automate Features**: If the team relies on specific Chef Automate features, finding equivalent functionality in the Ansible ecosystem may be challenging. Mitigation: Evaluate Ansible Tower/AWX as a replacement for Chef Automate's orchestration capabilities.

### Migration Order

1. **Ansible Playbooks** (Low risk): Refactor existing Ansible playbooks (`website_https.yml`, `poodle_fix.yml`) to use current best practices and collections
2. **Test Framework** (Medium risk): Migrate Test Kitchen to Molecule for testing infrastructure
3. **Compliance Testing** (Medium risk): Replace InSpec tests with Ansible-native compliance testing
4. **Chef Deployment Scripts** (High risk): Replace Chef Automate and Chef Infra Server deployment scripts with equivalent Ansible playbooks

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec integration with Ansible rather than being a production infrastructure codebase
2. The team is already familiar with Ansible as evidenced by existing playbooks
3. There are no external dependencies on Chef Automate or Chef Infra Server beyond what's shown in the deployment scripts
4. The compliance requirements currently addressed by InSpec will need equivalent coverage in the Ansible solution
5. The target environment will remain Ubuntu-based systems
6. The deployment scripts are used for setting up test/demo environments rather than production systems
7. There are no additional Chef cookbooks or resources beyond what's visible in the repository