# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for configuring HTTPS websites
2. Chef InSpec test profiles for compliance verification
3. Chef Automate and Chef Infra Server deployment scripts

The migration complexity is **LOW** with an estimated timeline of **1-2 weeks** for a single engineer. The primary focus will be on preserving the compliance testing capabilities while consolidating all infrastructure provisioning into Ansible.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS
    - Path: chef-and-ansible/website_https.yml (file)
    - Technology: Ansible
    - Key Features: SSL certificate generation, Apache configuration, virtual host setup

- **poodle-fix**:
    - Description: Ansible playbook that remediates the POODLE vulnerability in Apache SSL configuration
    - Path: chef-and-ansible/poodle_fix.yml (file)
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **chef-and-ansible-tests**:
    - Description: Directory containing Chef InSpec profiles for compliance testing
    - Path: chef-and-ansible/tests (directory)
    - Technology: Chef InSpec
    - Key Features: Contains website_https_verify.rb and ssh_profile.rb test files

- **setup-automate**:
    - Description: Directory containing deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate (directory)
    - Technology: Bash/Chef
    - Key Features: Contains deploy-automate.sh and deploy-chef-server.sh deployment scripts

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/index.html`: Sample HTML file for website testing
- `chef-and-ansible/README.md`: Documentation for the Chef InSpec with Ansible examples

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - Option 1: Use ansible-lint for basic compliance checks
  - Option 2: Integrate with Ansible Automation Platform's compliance capabilities
  - Option 3: Keep InSpec as a standalone tool and call it from Ansible

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - ansible-test for collection testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Automation Platform for centralized automation
  - AWX (open source upstream of Ansible Tower) for smaller deployments

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the POODLE fix playbook
  - Approach: Convert to an Ansible role that can be applied to multiple systems
  
- **SSH Hardening**: The SSH compliance profile checks for root login restrictions
  - Approach: Create an Ansible role that applies the same hardening and can be verified

- **Vault/secrets management**:
  - No encrypted secrets were found in the repository
  - Hardcoded credentials exist in the Chef server deployment scripts (username, password)
  - Migration should use Ansible Vault to secure these credentials

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible verification
  - Mitigation: Use the ansible.builtin.assert module or consider keeping InSpec for testing
  
- **Compliance Reporting**: Chef Automate provides compliance reporting that needs an equivalent
  - Mitigation: Implement Ansible Automation Platform with compliance capabilities or integrate with a third-party compliance tool

### Migration Order

1. **website-https** and **poodle-fix** playbooks (low risk, already in Ansible)
   - Convert to Ansible roles for better reusability
   - Implement idempotency improvements

2. **InSpec compliance tests** (moderate complexity)
   - Convert to Ansible assert tasks or maintain as InSpec tests called from Ansible

3. **Chef deployment scripts** (high complexity)
   - Replace with Ansible playbooks for deploying Ansible Automation Platform or AWX

### Assumptions

1. The primary goal is to consolidate on Ansible rather than maintain a hybrid Chef/Ansible environment
2. The InSpec tests are valuable and their functionality should be preserved
3. The deployment scripts are used for setting up test environments rather than production systems
4. No external Chef cookbooks or complex Chef-specific features are in use
5. The target environment will continue to be Ubuntu 20.04 or compatible systems
6. The security compliance requirements (STIG references in InSpec tests) must be maintained