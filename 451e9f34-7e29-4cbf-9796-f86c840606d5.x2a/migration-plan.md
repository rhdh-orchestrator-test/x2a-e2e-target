# MIGRATION FROM CHEF INSPEC TO ANSIBLE

This repository contains demonstration examples of Chef InSpec integration with Ansible rather than traditional Chef cookbooks. The migration scope is limited as the repository primarily contains Ansible playbooks with Chef InSpec verification tests, plus Chef server deployment scripts. The migration complexity is **LOW** with an estimated timeline of **1-2 weeks** for full conversion to native Ansible testing and deployment automation.

## Module Migration Plan

This repository contains Chef InSpec compliance tests and deployment scripts that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
No traditional infrastructure-as-code modules found in this repository. File searches confirmed the absence of:
- Chef cookbooks (no `recipes/default.rb` files found)
- Puppet modules (no `manifests/init.pp` files found) 
- PowerShell modules (no `.psd1` manifest files found)

This repository contains demonstration and testing code rather than deployable infrastructure modules.

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible provisioning with InSpec verification - needs conversion to molecule testing framework
- `website_https.yml`: Ansible playbook for Apache HTTPS setup - already in target format, requires only testing migration
- `poodle_fix.yml`: SSL security hardening playbook - already in target format
- `deploy-automate.sh`: Chef server deployment automation - needs conversion to Ansible playbook
- `deploy-chef-server.sh`: Standalone Chef server deployment - needs conversion to Ansible playbook
- `tests/website_https_verify.rb`: Chef InSpec compliance tests for HTTPS website verification
- `tests/ssh_profile.rb`: Chef InSpec compliance tests for SSH security hardening (STIG compliance)
- `index.html`: Static HTML test content for website verification

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml), with RHEL compatibility for STIG compliance requirements
- **Virtual Machine Technology**: Vagrant (configured in kitchen.yml for local testing)
- **Cloud Platform**: Not specified, but deployment scripts support both on-premises and cloud environments

## Migration Approach

### Key Dependencies to Address
- **Chef InSpec**: Replace with Ansible's built-in testing modules (assert, uri, service, etc.) or integrate with testinfra/pytest
- **Test Kitchen**: Replace with Molecule for Ansible role testing and verification
- **Chef Automate/Server**: Replace deployment scripts with Ansible playbooks using package management and configuration modules

### Security Considerations
- SSL/TLS certificate management: Current implementation uses self-signed certificates - migration should consider proper certificate authority integration
- SSH hardening compliance: STIG requirements (RHEL-08-000227) need to be maintained in Ansible format using security-focused roles
- Credential management: Deployment scripts contain hardcoded credentials that should be migrated to Ansible Vault
  - Username/password combinations in deployment scripts (userpassword='password')
  - SSL certificate and key file management
  - Chef organization validator keys

### Technical Challenges
- **InSpec to Native Testing**: Converting Chef InSpec compliance tests to Ansible's native testing capabilities or alternative testing frameworks
- **Test Kitchen Migration**: Replacing Test Kitchen workflow with Molecule for consistent testing methodology
- **Compliance Framework**: Maintaining STIG compliance verification without Chef InSpec dependency
- **Deployment Automation**: Converting bash-based Chef server deployment to idempotent Ansible playbooks

### Migration Order
1. **Testing Framework Migration** (low risk) - Convert Test Kitchen configuration to Molecule, replace InSpec tests with Ansible native testing
2. **Deployment Script Conversion** (moderate complexity) - Convert bash deployment scripts to Ansible playbooks with proper credential management
3. **Compliance Integration** (moderate complexity) - Implement STIG compliance checks using Ansible security modules or alternative testing frameworks

### Assumptions
- The repository serves as a demonstration/example rather than production infrastructure code
- Target environment will maintain Ubuntu/RHEL compatibility for existing compliance requirements
- Testing framework migration from Test Kitchen to Molecule is acceptable
- Chef InSpec compliance tests can be adequately replaced with Ansible native testing or alternative frameworks like testinfra
- Hardcoded credentials in deployment scripts are acceptable for demonstration purposes but should be vaulted in production migration
- SSL certificate management strategy (self-signed vs CA-issued) will be determined during migration implementation
- STIG compliance requirements must be maintained throughout the migration process
- No traditional Chef cookbooks exist in this repository, eliminating the need for recipe-to-playbook conversion