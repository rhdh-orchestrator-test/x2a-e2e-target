# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec compliance tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible compliance checks while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server setup scripts that need to be migrated to Ansible playbooks.

Estimated timeline: 1-2 weeks for a single developer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2 protocol

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled (STIG compliance)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, STIG compliance check

- **chef-automate-setup**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization setup

- **chef-server-setup**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework like Molecule.
- `index.html`: Simple HTML file used as a test page for the web server. Can be preserved as-is or converted to a template.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native compliance solutions:
  - Option 1: Convert InSpec tests to Ansible assert modules
  - Option 2: Use ansible-lint for static analysis
  - Option 3: Integrate with OpenSCAP via ansible-collection-compliance

- **Test Kitchen**: Replace with Molecule for Ansible role testing

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced and SSLv3 is disabled
  - Maintain compliance with security standards

- **SSH Security**: Preserve the SSH root login restriction check
  - Convert the InSpec control to an Ansible assert or ansible-lint rule

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates are generated dynamically but should use secure parameters

### Technical Challenges

- **InSpec to Ansible Conversion**: Converting InSpec tests to Ansible assertions requires careful mapping of test semantics
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules
  - Consider using ansible.posix and ansible.utils collections for system checks

- **Compliance Reporting**: InSpec provides rich compliance reporting that needs an equivalent in Ansible
  - Mitigation: Investigate integration with tools like OpenSCAP or Ansible AWX/Tower for compliance reporting

- **Chef Server Replacement**: The Chef Server setup scripts need to be replaced with equivalent infrastructure
  - Mitigation: Evaluate if Ansible AWX/Tower can provide the necessary functionality or if additional tools are needed

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format, may need minor updates for best practices
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert to Ansible assertions or integrate with compatible compliance tools
3. **Setup Scripts** (deploy-automate.sh, deploy-chef-server.sh): Convert to Ansible playbooks, addressing secret management

### Assumptions

1. The primary purpose of this repository is to demonstrate compliance automation using Chef InSpec alongside Ansible
2. The existing Ansible playbooks are functional and follow best practices
3. There is no requirement to maintain backward compatibility with Chef InSpec
4. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
5. The hardcoded credentials in the setup scripts are for demonstration purposes only and will be properly secured in the migration
6. The self-signed certificates are acceptable for the use case and don't need to be replaced with CA-signed certificates
7. The STIG compliance requirements in the ssh_profile.rb need to be maintained in the Ansible implementation