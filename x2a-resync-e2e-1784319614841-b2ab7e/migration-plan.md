# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec test profiles for verifying compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing functionality while consolidating all infrastructure provisioning into Ansible.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook for configuring Apache with HTTPS
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook for remediating SSL POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website-https-verify**:
    - Description: Chef InSpec test profile for verifying HTTPS website configuration
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port, HTTP response, and SSL protocol verification

- **ssh-profile**:
    - Description: Chef InSpec test profile for SSH security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification with STIG references

- **chef-automate-deploy**:
    - Description: Shell script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate and Chef Infra Server installation and configuration

- **chef-server-deploy**:
    - Description: Shell script for deploying Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation and configuration

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file for website testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - Option 1: Use ansible-lint for basic compliance checks
  - Option 2: Integrate with Ansible Automation Platform's compliance capabilities
  - Option 3: Convert InSpec tests to equivalent Ansible assert tasks

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - ansible-test for collection testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Automation Platform for centralized automation
  - AWX (open source version of Ansible Tower) if budget constraints exist

### Security Considerations

- **SSL Configuration**: The migration must preserve the SSL hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced
  - Disable older protocols (SSL3, TLS 1.0, TLS 1.1)

- **SSH Hardening**: Maintain the SSH security controls from the InSpec profile
  - Disable root login via SSH
  - Preserve STIG compliance requirements

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - SSL certificates generated in the Ansible playbook
  - Recommend migration to Ansible Vault for credential storage

### Technical Challenges

- **InSpec to Ansible Conversion**: Converting InSpec tests to Ansible assertions or checks
  - Mitigation: Use ansible.builtin.assert module with appropriate conditions
  - Consider ansible-lint custom rules for ongoing compliance

- **Compliance Reporting**: Replacing Chef InSpec reporting capabilities
  - Mitigation: Implement structured output collection in Ansible
  - Consider integration with compliance tools like OpenSCAP

- **Chef Automate Functionality**: Replacing Chef Automate's compliance dashboard
  - Mitigation: Evaluate Ansible Automation Platform's compliance capabilities
  - Consider complementary tools like Prometheus/Grafana for visualization

### Migration Order

1. Ansible Playbooks (website_https.yml, poodle_fix.yml) - Low risk, already in Ansible format
2. InSpec Tests (website_https_verify.rb, ssh_profile.rb) - Convert to Ansible assertions
3. Chef Deployment Scripts (deploy-automate.sh, deploy-chef-server.sh) - Replace with Ansible roles

### Assumptions

1. The primary purpose of this repository is demonstration/educational rather than production use
2. The InSpec tests are used for verification only and not for remediation
3. There are no external dependencies on Chef Automate beyond what's in the deployment scripts
4. The target environment will continue to be Ubuntu 20.04 or compatible
5. No complex state management or data persistence is required
6. The migration will consolidate on Ansible rather than maintaining a hybrid approach
7. No custom Chef resources or complex Chef-specific functionality is in use
8. The SSL and Apache configurations are relatively standard and can be directly mapped to Ansible modules