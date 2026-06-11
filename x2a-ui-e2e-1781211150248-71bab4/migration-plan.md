# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, primarily involving:

1. Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec tests for compliance verification
3. Chef Automate and Chef Infra Server deployment scripts

The migration complexity is **LOW** with an estimated timeline of **1-2 weeks** due to the limited number of components and the fact that part of the infrastructure is already using Ansible.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https-configuration**:
    - Description: Ansible playbook for configuring Apache web server with HTTPS, self-signed certificates, and basic website deployment
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **ssl-poodle-fix**:
    - Description: Ansible playbook for remediating SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **https-compliance-tests**:
    - Description: Chef InSpec tests for verifying HTTPS configuration, port availability, and SSL protocol security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port testing, HTTP response validation, SSL protocol verification

- **ssh-security-profile**:
    - Description: Chef InSpec profile for SSH security compliance checking, specifically root login restrictions
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance checks with STIG references

- **chef-infrastructure-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash with Chef CLI tools
    - Key Features: Chef server deployment, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `index.html`: Sample HTML file used for website testing

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be infrastructure-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - Option 1: Use ansible-lint for basic compliance checking
  - Option 2: Integrate with Ansible Automation Platform's compliance capabilities
  - Option 3: Convert InSpec tests to equivalent Ansible assert tasks or custom modules

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role and playbook testing
  - ansible-test for collection testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Automation Platform for centralized automation
  - AWX (open source upstream of Ansible Tower) if budget constraints exist

### Security Considerations

- **SSL Configuration**: The poodle_fix.yml playbook enforces TLSv1.2 only. Ensure this security hardening is maintained in the migrated solution.
  
- **SSH Security**: The ssh_profile.rb InSpec test verifies SSH root login is disabled. This compliance check should be maintained in the Ansible solution.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates are generated in the playbook - consider using ansible-vault for storing private keys

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible verification methods will require careful mapping of test assertions to Ansible modules or custom scripts.
  - Mitigation: Use assert module in Ansible for basic tests, and consider custom modules for more complex validations

- **Chef Server Deployment**: The Chef server deployment scripts need to be replaced with equivalent Ansible infrastructure.
  - Mitigation: Deploy Ansible Automation Platform or AWX using Ansible playbooks

### Migration Order

1. **website-https-configuration** (Priority 1 - already Ansible, just needs refinement)
   - Update to use Ansible best practices
   - Implement idempotency improvements
   - Add proper error handling

2. **ssl-poodle-fix** (Priority 1 - already Ansible, just needs refinement)
   - Integrate with the main website playbook
   - Improve variable handling

3. **InSpec Tests** (Priority 2 - requires conversion)
   - Convert website_https_verify.rb to Ansible assert tasks
   - Convert ssh_profile.rb to Ansible security checks

4. **Chef Infrastructure Deployment** (Priority 3 - requires replacement)
   - Create Ansible playbooks for deploying Ansible Automation Platform or AWX

### Assumptions

1. The primary goal is to consolidate on Ansible as the single automation tool, eliminating Chef components
2. The InSpec tests are valuable and their functionality should be preserved in Ansible
3. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs
4. The deployment scripts for Chef infrastructure will be replaced with equivalent Ansible infrastructure
5. No specific performance requirements are mentioned that might affect the migration approach
6. No external integrations or APIs are referenced that would need special handling
7. The security compliance requirements (STIG references in ssh_profile.rb) must be maintained in the Ansible solution